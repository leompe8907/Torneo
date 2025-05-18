from django.contrib import admin
from .models import Registro, Torneo, Inscripciones, Partidas

# Register your models here.
admin.site.register(Registro)
admin.site.register(Torneo)
admin.site.register(Inscripciones)
admin.site.register(Partidas)