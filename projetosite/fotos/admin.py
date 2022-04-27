from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from .models import Foto, Categoria, Utilizador


admin.site.register(Categoria)
admin.site.register(Foto)