# Generated by Django 5.2.1 on 2025-05-18 17:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Torneo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50, unique=True)),
                ('descripcion', models.CharField(max_length=200)),
                ('modo', models.CharField(choices=[('Estándar', 'Estándar'), ('Rapido', 'Rapido'), ('Blitz', 'Blitz'), ('Bullet', 'Bullet')], max_length=10)),
                ('fecha_creacion', models.DateField(auto_now_add=True)),
                ('fecha_inicio', models.DateField()),
                ('hora_inicio', models.TimeField()),
                ('integrantes', models.IntegerField()),
                ('premio', models.IntegerField()),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('en_curso', 'En Curso'), ('finalizada', 'Finalizada')], default='pendiente', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Registro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=50)),
                ('alias', models.CharField(max_length=50, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('puntos', models.IntegerField(default=0)),
                ('elo', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Partidas',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('en_curso', 'En Curso'), ('finalizada', 'Finalizada')], default='pendiente', max_length=10)),
                ('fecha', models.DateField(auto_now_add=True)),
                ('participante1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participante1', to=settings.AUTH_USER_MODEL)),
                ('participante2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participante2', to=settings.AUTH_USER_MODEL)),
                ('torneo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='torneo.torneo')),
            ],
        ),
        migrations.CreateModel(
            name='Inscripciones',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('participante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('torneo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='torneo.torneo')),
            ],
        ),
    ]
