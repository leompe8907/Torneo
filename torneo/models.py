from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UsuarioManager(BaseUserManager):
    def create_user(self, email, contraseña=None, **extra_fields):
        if not email:
            raise ValueError('El correo es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(contraseña)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, contraseña=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, contraseña, **extra_fields)

class Registro(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    alias = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    puntos = models.IntegerField(default=0)
    elo = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'alias']

    def __str__(self):
        return self.email


class Torneo(models.Model):
    Modo = [
        ('Estándar', 'Estándar'),
        ('Rapido', 'Rapido'),
        ('Blitz', 'Blitz'),
        ('Bullet', 'Bullet'),
    ]
    
    ESTADO = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En Curso'),
        ('finalizada', 'Finalizada'),
    ]
    
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=False, null=False, unique=True)
    descripcion = models.CharField(max_length=200, blank=False, null=False)
    modo = models.CharField(max_length=10, choices=Modo, blank=False, null=False)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_inicio = models.DateField(blank=False, null=False)
    hora_inicio = models.TimeField(blank=False, null=False)
    integrantes = models.IntegerField(blank=False, null=False)
    premio = models.IntegerField(blank=False, null=False)
    estado = models.CharField(max_length=10, choices=ESTADO, default='pendiente')

class Inscripciones(models.Model):
    id = models.AutoField(primary_key=True)
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    participante = models.ForeignKey(Registro, on_delete=models.CASCADE)

class Partidas(models.Model):
    ESTADOS_PARTIDA = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En Curso'),
        ('finalizada', 'Finalizada'),
    ]

    id = models.AutoField(primary_key=True)
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    participante1 = models.ForeignKey(Registro, on_delete=models.CASCADE, related_name='participante1')
    participante2 = models.ForeignKey(Registro, on_delete=models.CASCADE, related_name='participante2')
    ronda = models.IntegerField(default=1)
    ganador = models.ForeignKey(Registro, on_delete=models.CASCADE, related_name='ganador', null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS_PARTIDA, default='pendiente')
    fecha = models.DateField(auto_now_add=True)