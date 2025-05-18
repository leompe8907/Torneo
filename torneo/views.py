from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import RegistroSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class RegistroView(APIView):
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response({'mensaje': f'El usuario {usuario.nombre} fue registrado con éxito'}, status=201)
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.validated_data['usuario']
            refresh = RefreshToken.for_user(usuario)
            return Response({
                'mensaje': 'Login exitoso',
                'usuario': {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'email': usuario.email
                },
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        return Response(serializer.errors, status=400)
