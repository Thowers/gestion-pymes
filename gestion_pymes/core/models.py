from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('cajero', 'Cajero'),
    ]
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='cajero')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def es_admin(self):
        return self.rol == 'admin'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"
