from django.urls import path
from .views import RegistroView, LoginView, TorneoView, InscribirseTorneoAPIView, ParticipantesPorTorneoAPIView, EmparejamientosAPIView, FinalizarPartidaAPIView, RondasPorTorneoAPIView

urlpatterns = [
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('torneos/', TorneoView.as_view(),name='torneos'),
    path('torneos/<int:torneo_id>/inscribirse/', InscribirseTorneoAPIView.as_view(), name='inscribirse_torneo'),
    path('torneos/<int:torneo_id>/participantes/', ParticipantesPorTorneoAPIView.as_view(), name='participantes_torneo'),
    path('torneos/<int:torneo_id>/emparejamientos/', EmparejamientosAPIView.as_view(), name='emparejar_participantes'),
    path('partidas/<int:partida_id>/finalizar/', FinalizarPartidaAPIView.as_view(), name='finalizar_partida'),
    path('torneos/<int:torneo_id>/rondas/', RondasPorTorneoAPIView.as_view(), name='rondas_por_torneo'),

]
