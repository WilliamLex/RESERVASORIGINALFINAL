import re
from django.db import models
from django.core import validators
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, UserManager
)


class User(AbstractBaseUser, PermissionsMixin):
    
    username = models.CharField(
        'Usuario', max_length=30, unique=True, validators=[
            validators.RegexValidator(
                re.compile('^[\w.@+-]+$'),
                'Proporcione un nombre de usuario válido. '
                'Este valor debe contener solo letras, números '
                'y los caracteres: @/./+/-/_.'
                ,  'inválido'
            )
        ], help_text='Un nombre corto que se utilizará'+
                    ' para identificarte de manera única en la plataforma.'
    )
    
    name = models.CharField('Nombre', max_length=100)
    email = models.EmailField('Correo Electrónico', unique=True)
    is_staff = models.BooleanField('Personal', default=False)
    is_active = models.BooleanField('Activo', default=True)
    date_joined = models.DateTimeField('Fecha de Ingreso', auto_now_add=True)


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.name or self.username
    
    def get_full_name(self):
        return str(self)

    def get_short_name(self):
        return str(self).split(' ')[0]
