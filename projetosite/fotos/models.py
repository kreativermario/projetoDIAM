from django.db import models

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

