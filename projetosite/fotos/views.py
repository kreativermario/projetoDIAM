from django.shortcuts import render

# Create your views here.

def galeria(request):
    return render(request, 'fotos/galeria.html')


def verFoto(request, pk):
    return render(request, 'fotos/foto.html')


def criarFoto(request):
    return render(request, 'fotos/criar.html')
