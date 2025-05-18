from django.urls import path
from .views import RegistroView, LoginView

urlpatterns = [
    path('registro/', RegistroView.as_view()),
    path('login/', LoginView.as_view()),
]
