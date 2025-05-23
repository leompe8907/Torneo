from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.shortcuts import get_object_or_404
from django.utils import timezone

from datetime import datetime

import random

from .serializer import RegistroSerializer, LoginSerializer, TorneoSerializer, InscripcionesSerializer
from .models import Torneo, Inscripciones, Partidas, Registro


class RegistroView(APIView):
    """
    Permite registrar nuevos usuarios en el sistema. Valida los campos requeridos, 
    incluidas contraseñas coincidentes y alias únicos. Al finalizar, 
    retorna un mensaje de éxito junto con los datos del nuevo usuario.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response({'mensaje': f'El usuario {usuario.nombre} fue registrado con éxito'}, status=201)
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    """
        Autentica a un usuario mediante correo y contraseña. 
        Si las credenciales son válidas, genera y retorna un par de tokens JWT (access y refresh) 
        junto con los datos básicos del usuario autenticado.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.validated_data['usuario']
            refresh = RefreshToken.for_user(usuario)
            return Response({
                'mensaje': f'Bienvenido {usuario.nombre}',
                'usuario': {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'email': usuario.email
                },
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        return Response(serializer.errors, status=400)

class TorneoView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        """
            Crea un nuevo torneo con los datos recibidos. 
            Requiere autenticación y valida los campos obligatorios como nombre, fecha de inicio, modo, etc.
        """
        serializer = TorneoSerializer(data=request.data)
        if serializer.is_valid():
            torneo = serializer.save()
            return Response({'mensaje': f'El torneo {torneo.nombre} fue creado con éxito'}, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        """
            Lista todos los torneos existentes. 
            Además, actualiza automáticamente el estado de cada torneo dependiendo de la fecha/hora actual 
            y el progreso de las partidas (pasando de pendiente a en_curso o finalizada).
        """
        
        torneos = Torneo.objects.all()

        for torneo in torneos:
            ahora = timezone.now()
            fecha_hora_inicio = timezone.make_aware(datetime.combine(torneo.fecha_inicio, torneo.hora_inicio))

            # Cambiar de pendiente a en_curso
            if torneo.estado == 'pendiente' and ahora >= fecha_hora_inicio:
                torneo.estado = 'en_curso'
                torneo.save()

            # Cambiar de en_curso a finalizada si todas las partidas terminaron
            if torneo.estado == 'en_curso':
                partidas = Partidas.objects.filter(torneo=torneo)
                if partidas.exists() and all(p.estado == 'finalizada' for p in partidas):
                    torneo.estado = 'finalizada'
                    torneo.save()

        serializer = TorneoSerializer(torneos, many=True)
        return Response(serializer.data, status=200)

class InscribirseTorneoAPIView(APIView):
    """
        Permite que un usuario autenticado se inscriba a un torneo, si:

            - El torneo está en estado pendiente.
            - No está ya inscrito en ese torneo.
            - No está inscrito en otro torneo el mismo día.
            - Aún hay cupo disponible (según torneo.integrantes).

        Retorna los datos de la inscripción si se realiza exitosamente.
    
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, torneo_id):
        try:
            torneo = Torneo.objects.get(id=torneo_id)
        except Torneo.DoesNotExist:
            return Response({"error": "Torneo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        usuario = request.user

        # 1. Validar estado del torneo
        if torneo.estado != 'pendiente':
            return Response({"error": "Solo puedes inscribirte en torneos pendientes"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Validar si ya está inscrito en este torneo
        if Inscripciones.objects.filter(torneo=torneo, participante=usuario).exists():
            return Response({"error": "Ya estás inscrito en este torneo"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Validar si está inscrito en otro torneo ese día
        fecha = torneo.fecha_inicio
        ya_inscrito = Inscripciones.objects.filter(
            participante=usuario,
            torneo__fecha_inicio=fecha
        ).exists()

        if ya_inscrito:
            return Response(
                {"error": "Ya estás inscrito en otro torneo en la misma fecha"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Validar si ya se llenó el cupo
        inscritos = Inscripciones.objects.filter(torneo=torneo).count()
        if inscritos >= torneo.integrantes:
            return Response({"error": "El torneo ya alcanzó el número máximo de participantes"}, status=status.HTTP_400_BAD_REQUEST)

        # Si todo está OK, inscribir
        inscripcion = Inscripciones.objects.create(torneo=torneo, participante=usuario)
        serializer = InscripcionesSerializer(inscripcion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ParticipantesPorTorneoAPIView(APIView):
    """
        Retorna la lista de participantes inscritos en un torneo específico. 
        Por cada participante incluye su nombre, ELO y puntos acumulados.
    """
    
    permission_classes = [IsAuthenticated]

    def get(self, request, torneo_id):
        torneo = get_object_or_404(Torneo, id=torneo_id)
        inscripciones = Inscripciones.objects.filter(torneo=torneo)

        participantes_info = [
            {
                "nombre": i.participante.nombre,
                "elo": i.participante.elo,
                "puntos": i.participante.puntos
            }
            for i in inscripciones
        ]

        return Response(participantes_info, status=status.HTTP_200_OK)

class EmparejamientosAPIView(APIView):
    
    """
        Genera los emparejamientos de una nueva ronda del torneo:

            - En la primera ronda, empareja a todos los inscritos aleatoriamente.
            - En rondas siguientes, empareja solo a los ganadores de la ronda anterior.
            - Si hay un número impar de jugadores, uno queda libre y pasa automáticamente.
            - Registra cada partida como un objeto Partidas, indicando su ronda y estado.
    """
    
    permission_classes = [IsAuthenticated]

    def post(self, request, torneo_id):
        torneo = Torneo.objects.filter(id=torneo_id).first()
        if not torneo:
            return Response({"error": "Torneo no encontrado"}, status=404)

        # Buscar la última ronda
        ultima_ronda = Partidas.objects.filter(torneo=torneo).aggregate(models.Max('ronda'))['ronda__max'] or 0
        nueva_ronda = ultima_ronda + 1

        if nueva_ronda == 1:
            # Primera ronda: tomar todos los inscritos
            participantes = [i.participante for i in Inscripciones.objects.filter(torneo=torneo)]
        else:
            # Rondas siguientes: tomar ganadores de la ronda anterior
            partidas_anteriores = Partidas.objects.filter(torneo=torneo, ronda=ultima_ronda)
            if partidas_anteriores.filter(estado='finalizada').count() != partidas_anteriores.count():
                return Response({"error": "Aún hay partidas pendientes en la ronda anterior"}, status=400)

            participantes = []
            for partida in partidas_anteriores:
                if partida.ganador:
                    participantes.append(partida.ganador)

        if len(participantes) < 2:
            return Response({"mensaje": "No hay suficientes participantes para una nueva ronda"}, status=200)

        random.shuffle(participantes)
        emparejamientos = []

        for i in range(0, len(participantes) - 1, 2):
            p1 = participantes[i]
            p2 = participantes[i + 1]
            partida = Partidas.objects.create(
                torneo=torneo,
                participante1=p1,
                participante2=p2,
                estado='pendiente',
                ronda=nueva_ronda
            )
            emparejamientos.append({
                "partida_id": partida.id,
                "ronda": nueva_ronda,
                "participante1": p1.nombre,
                "participante2": p2.nombre
            })

        # Si hay un impar, queda libre para próxima ronda
        if len(participantes) % 2 == 1:
            libre = participantes[-1]
            emparejamientos.append({
                "partida_id": None,
                "ronda": nueva_ronda,
                "mensaje": f"{libre.nombre} queda libre esta ronda y pasa automáticamente"
            })

        return Response(emparejamientos, status=201)

class FinalizarPartidaAPIView(APIView):
    """
        Permite registrar el resultado de una partida, marcándola como finalizada y asignando un ganador.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, partida_id):
        partida = get_object_or_404(Partidas, id=partida_id)

        ganador_id = request.data.get('ganador_id')
        if not ganador_id:
            return Response({"error": "Debe proporcionar el ID del ganador"}, status=400)

        if ganador_id not in [partida.participante1.id, partida.participante2.id]:
            return Response({"error": "El ganador debe ser uno de los participantes"}, status=400)

        ganador = get_object_or_404(Registro, id=ganador_id)
        partida.ganador = ganador
        partida.estado = 'finalizada'
        partida.save()

        return Response({
            "mensaje": "Partida finalizada",
            "partida_id": partida.id,
            "ganador": ganador.nombre
        }, status=200)

class RondasPorTorneoAPIView(APIView):
    """
        Devuelve una estructura ordenada por rondas que muestra todas las partidas de un torneo. 
        Por cada partida muestra: ID, nombres de los jugadores, estado actual y ganador si ya fue definido.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, torneo_id):
        torneo = get_object_or_404(Torneo, id=torneo_id)
        partidas = Partidas.objects.filter(torneo=torneo).select_related('participante1', 'participante2', 'ganador')

        rondas_dict = {}
        for partida in partidas:
            ronda = partida.ronda
            if ronda not in rondas_dict:
                rondas_dict[ronda] = []

            rondas_dict[ronda].append({
                "id": partida.id,
                "participante1": partida.participante1.nombre,
                "participante2": partida.participante2.nombre,
                "estado": partida.estado,
                "ganador": partida.ganador.nombre if partida.ganador else None
            })

        resultado = [
            {"ronda": ronda, "partidas": rondas_dict[ronda]}
            for ronda in sorted(rondas_dict.keys())
        ]

        return Response(resultado, status=200)
