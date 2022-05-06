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
    autor = models.ForeignKey(User, on_delete=models.CASCADE, default="")

    def number_of_likes(self):
        return self.likes.count()

    class Meta:
        ordering = ('created_date',)


class Comentario(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE, default="")
    texto = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    foto = models.ForeignKey(Foto, on_delete=models.CASCADE)



class Utilizador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_img = models.ImageField(upload_to='profile/', blank=True)
    about = models.CharField(max_length=250, null=True, blank=True)

    def image_url(self):
        if self.profile_img and hasattr(self.profile_img, 'url'):
            return self.profile_img.url
        else:
            return '/static/images/profile/default.jpg'

    class Meta:
        permissions = [
            ("criar_post", "Pode criar posts"),
            ("criar_like_dislike", "Pode dar likes ou dislikes"),
            ("criar_comentario", "Pode criar comentários"),
        ]

