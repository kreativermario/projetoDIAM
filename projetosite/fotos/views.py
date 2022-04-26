from django.shortcuts import render
from .models import Categoria, Foto
# Create your views here.

def galeria(request):
    categorias = Categoria.objects.all()
    fotos = Foto.objects.all()
    context = {
        'categorias': categorias,
        'fotos' : fotos
    }

    return render(request, 'fotos/galeria.html', context)


def verFoto(request, pk):
    foto = Foto.objects.get(id=pk)
    context = {
        'foto': foto
    }
    return render(request, 'fotos/foto.html', context)


def criarFoto(request):
    categorias = Categoria.objects.all()
    context = {
        'categorias': categorias,
    }
    return render(request, 'fotos/criar.html', context)
