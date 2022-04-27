from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.core.validators import MinValueValidator, MinLengthValidator, MaxLengthValidator
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Categoria(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nome


class Foto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    imagem = models.ImageField(null=False, blank=False)
    titulo = models.CharField(max_length=250, null=False, blank=False)
    descricao = models.TextField()
    created_date = models.DateTimeField(default=now)
    likes = models.ManyToManyField(User, related_name='fotos_like')
    author = models.ForeignKey(User, on_delete=models.CASCADE, default="")

    def number_of_likes(self):
        return self.likes.count()

    class Meta:
        ordering = ('created_date',)


class Utilizador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_img = models.ImageField(blank = True, null=True)

    class Meta:
        permissions = [
            ("criar_post", "Pode criar posts"),
        ]

