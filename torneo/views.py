from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import BasicAuthentication

from django.shortcuts import get_object_or_404

from .serializer import RegistroSerializer, LoginSerializer, TorneoSerializer, InscripcionesSerializer
from .models import Torneo, Inscripciones


class RegistroView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response({'mensaje': f'El usuario {usuario.nombre} fue registrado con éxito'}, status=201)
        return Response(serializer.errors, status=400)
class LoginView(APIView):
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
        serializer = TorneoSerializer(data=request.data)
        if serializer.is_valid():
            torneo = serializer.save()
            return Response({'mensaje': f'El torneo {torneo.nombre} fue creado con éxito'}, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        torneos = Torneo.objects.all()
        if torneos.exists():
            serializer = TorneoSerializer(torneos, many=True)
            return Response(serializer.data, status=200)
        return Response({'mensaje': 'No hay torneos disponibles'}, status=404)

class InscribirseTorneoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, torneo_id):
        try:
            torneo = Torneo.objects.get(id=torneo_id)
        except Torneo.DoesNotExist:
            return Response({"error": "Torneo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        usuario = request.user

        # Buscar si ya está inscrito en otro torneo el mismo día
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

        # Si no está inscrito, crear la inscripción
        inscripcion = Inscripciones.objects.create(torneo=torneo, participante=usuario)
        serializer = InscripcionesSerializer(inscripcion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ParticipantesPorTorneoAPIView(APIView):
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
    permission_classes = [IsAuthenticated]

    def post(self, request, torneo_id):
        torneo = get_object_or_404(Torneo, id=torneo_id)
        inscripciones = Inscripciones.objects.filter(torneo=torneo).select_related('participante')

        if inscripciones.count() < 2:
            return Response({"error": "Se requieren al menos 2 participantes para emparejar."}, status=400)

        participantes = sorted(
            [i.participante for i in inscripciones],
            key=lambda p: (-p.puntos, -float(p.elo))  # mayor puntaje y elo primero
        )

        emparejamientos = []
        for i in range(0, len(participantes) - 1, 2):
            p1 = participantes[i]
            p2 = participantes[i+1]
            partida = Partidas.objects.create(
                torneo=torneo,
                participante1=p1,
                participante2=p2,
                estado='pendiente'
            )
            emparejamientos.append({
                "partida_id": partida.id,
                "participante1": p1.nombre,
                "participante2": p2.nombre
            })

        return Response(emparejamientos, status=201)