from rest_framework import serializers
from models import Registro, Torneo, Inscripciones, Partidas

class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registro
        fields = '__all__'

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