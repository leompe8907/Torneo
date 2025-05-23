from rest_framework import serializers
from .models import Registro, Torneo, Inscripciones, Partidas

class RegistroSerializer(serializers.ModelSerializer):
    contraseña = serializers.CharField(write_only=True)
    confirmar_contraseña = serializers.CharField(write_only=True)

    class Meta:
        model = Registro
        fields = ['id', 'nombre', 'apellido', 'alias', 'email', 'contraseña', 'confirmar_contraseña']

    def validate(self, data):
        if data['contraseña'] != data['confirmar_contraseña']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data
    
    def validate_alias(self, value):
        if Registro.objects.filter(alias=value).exists():
            raise serializers.ValidationError("Este alias ya está en uso.")
        return value

    def create(self, validated_data):
        validated_data.pop('confirmar_contraseña')
        contraseña = validated_data.pop('contraseña')
        user = Registro(**validated_data)
        user.set_password(contraseña)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    contraseña = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        usuario = authenticate(email=data['email'], password=data['contraseña'])
        if not usuario:
            if not Registro.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError("El usuario no está registrado.")
            raise serializers.ValidationError("La contraseña es incorrecta.")
        data['usuario'] = usuario
        return data



class TorneoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Torneo
        fields = '__all__'

class InscripcionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscripciones
        fields = '__all__'

class PartidasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partidas
        fields = '__all__'