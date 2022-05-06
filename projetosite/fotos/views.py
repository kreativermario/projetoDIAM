import os
from django.db.models import Q
import django.urls
from django.views import View
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Categoria, Foto, Utilizador, Comentario
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from .forms import RegisterForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
def no_perms_page(request):
    return render(request, 'fotos/no_perms.html')


# Ver se tem permissões!
def is_member(user):
    return user.groups.filter(name='utilizadores').exists()


def delete_profile_img(utilizador):
    if utilizador.image_url != '/static/images/profile/default.jpg':
        utilizador.profile_img.delete()


# Frontpage
def index(request):
    categoria = request.GET.get('categoria')
    if categoria is None:
        fotos = Foto.objects.all()
    else:
        # Aplicar filtro
        fotos = Foto.objects.filter(categoria__nome__contains=categoria)


    categorias = Categoria.objects.all()
    context = {
        'categorias': categorias,
        'fotos' : fotos
    }

    return render(request, 'fotos/index.html', context)


# Galeria
def galeria(request):
    # Filtro de categoria
    categoria = request.GET.get('categoria')
    # Filtro de sort
    sort = request.GET.get('sort')
    # Filtro de pesquisa
    pesquisa = request.GET.get('q')

    # Todas as categorias
    categorias = Categoria.objects.all()

    # Se não for dado filtro de categoria
    if categoria is None:
        fotos = Foto.objects.all()
    # Aplicar filtro de categoria
    else:
        fotos = Foto.objects.filter(categoria__nome__contains=categoria)
    # Aplicar filtro de sort
    if sort is not None:

        # Sort ascendente por data
        if sort == 'dataAscendente':
            fotos = Foto.objects.order_by('created_date')

        # Sort decrescente por data
        elif sort == 'dataDecrescente':
            fotos = Foto.objects.order_by('-created_date')

        # Sort por likes decrescente
        else:
            unsorted_fotos = fotos.all()
            fotos = sorted(unsorted_fotos, key=lambda t: t.number_of_likes(), reverse=True)

    # Filtro por pesquisa
    if pesquisa is not None:
        fotos = Foto.objects.filter(Q(titulo__icontains=pesquisa) | Q(autor__username__icontains=pesquisa))

    context = {
        'categorias': categorias,
        'fotos': fotos
    }

    return render(request, 'fotos/galeria.html', context)


def comunidade(request):
    utilizadores = Utilizador.objects.all()

    context = {
        'utilizadores': utilizadores
    }

    return render(request, 'fotos/comunidade.html', context)


def process_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    foto_id = comentario.foto.id
    if comentario.autor == request.user:
        comentario.delete()

    return redirect('fotos:foto', foto_id)


def removerFoto(request, pk):
    foto = get_object_or_404(Foto, pk=pk)
    if foto.autor == request.user or request.user.is_superuser:
        foto.delete()
        return redirect('fotos:galeria')
    # Fazer 'refresh' para a página anterior que era esta
    return redirect(request.META['HTTP_REFERER'])


def verFoto(request, pk):
    foto = get_object_or_404(Foto, pk=pk)
    comentarios = Comentario.objects.filter(foto_id=pk).order_by('-created_date')
    likes = foto.number_of_likes()
    is_allowed = is_member(request.user)
    is_autor = False
    if foto.autor == request.user:
        is_autor = True
    liked = False

    if foto.likes.filter(id=request.user.id).exists():
        liked = True

    # Likes e Dislikes
    if request.method == 'POST':
        if request.POST.get('like') is not None:
            if foto.likes.filter(id=request.user.id).exists():
                liked = True
                context = {
                    'foto': foto,
                    'likes': likes,
                    'foto_is_liked': liked,
                    'is_allowed': is_allowed,
                    'comentarios': comentarios,
                    'is_autor': is_autor,
                }
            else:
                foto.likes.add(request.user)
        if request.POST.get('dislike') is not None:
            if foto.likes.filter(id=request.user.id).exists():
                foto.likes.remove(request.user)
        # Comentário
        if request.POST.get('texto') is not None:
            texto = request.POST.get('texto')
            comentario = Comentario(
                autor=request.user,
                texto=texto,
                foto=foto
            )
            comentario.save()

        # Fazer 'refresh' para a página anterior que era esta
        return redirect(request.META['HTTP_REFERER'])

    context = {
        'foto': foto,
        'likes': likes,
        'foto_is_liked': liked,
        'is_allowed': is_allowed,
        'comentarios': comentarios,
        'is_autor': is_autor,
    }

    return render(request, 'fotos/foto.html', context)


@login_required(login_url=reverse_lazy('fotos:login'))
@user_passes_test(is_member, login_url=reverse_lazy('fotos:no_perms_page'))
def criarFoto(request):
    categorias = Categoria.objects.all()

    if request.method == 'POST':
        data = request.POST
        imagem = request.FILES.get('imagem')
        titulo = data['titulo']
        descricao = data['descricao']
        if data['categoria'] != "none":
            categoria = Categoria.objects.get(id=data['categoria'])
        elif data['novaCategoria'] != '':
            # Cria uma categoria se já não existir.
            # Se já existir, faz um get e coloca na variavel categoria
            categoria, novaCategoria = Categoria.objects.get_or_create(nome=data['novaCategoria'])
        else:
            categoria = None

        foto = Foto.objects.create(
            categoria = categoria,
            titulo = titulo,
            descricao = descricao,
            imagem = imagem,
            autor = request.user
        )

        return redirect('fotos:galeria')

    context = {
        'categorias': categorias,
    }
    return render(request, 'fotos/criar.html', context)


def registar(request):
    template = 'fotos/registar.html'

    if request.method == 'POST':

        form = RegisterForm(request.POST)
        foto_perfil = request.FILES.get('foto_perfil')
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                return render(request, template, {
                    'form': form,
                    'error_message': 'Username já existe.'
                })
            elif User.objects.filter(email=form.cleaned_data['email']).exists():
                return render(request, template, {
                    'form': form,
                    'error_message': 'Email já existe.'
                })
            elif form.cleaned_data['password'] != form.cleaned_data['password_repeat']:
                return render(request, template, {
                    'form': form,
                    'error_message': 'Passwords não coincidem.'
                })
            else:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['primeiro_nome'],
                    last_name=form.cleaned_data['ultimo_nome'],
                    password=form.cleaned_data['password'],
                )
                utilizador = Utilizador(user=user, profile_img=foto_perfil)
                group = Group.objects.get(name='utilizadores')
                user.groups.add(group)
                utilizador.save()
                # Login
                login(request, user)

                return redirect('fotos:galeria')

    else:
        form = RegisterForm()

    return render(request, template, {'form': form})


def user_login(request):
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:

            login(request, user)
            return redirect('fotos:galeria')

        else:
            return render(request, 'fotos/login.html', {'error_message': 'Username e/ou password incorretos!'})

    else:
        return render(request, 'fotos/login.html')


@login_required(login_url=reverse_lazy('fotos:login'))
def process_logout(request):
    logout(request)
    return redirect('fotos:login')


@login_required(login_url=reverse_lazy('fotos:login'))
def profile(request):
    likes_count = 0
    fotos = Foto.objects.all()
    fotos_autor = fotos.filter(autor=request.user.id)
    autor_count = fotos_autor.count()
    for foto in fotos:
        likes_count += foto.likes.filter(id=request.user.id).count()

    context = {
        "fotos": fotos_autor,
        "likes_count": likes_count,
        "autor_count": autor_count
    }
    return render(request, 'fotos/profile.html', context)


@login_required(login_url=reverse_lazy('fotos:login'))
def profile_edit(request):

    if request.method == 'POST':
        data = request.POST
        user = request.user
        utilizador = Utilizador.objects.get(user_id=request.user.id)
        imagem = request.FILES.get('profile_img')
        background_img = request.FILES.get('background_img')
        primeiro_nome= data['primeiro_nome']
        ultimo_nome = data['ultimo_nome']
        about = data['sobre_mim']
        print(request.POST)
        if primeiro_nome != "":
            user.first_name = primeiro_nome
        if ultimo_nome != "":
            user.last_name = ultimo_nome
        if about != "":
            utilizador.about = about
        if imagem is not None:
            delete_profile_img(utilizador)
            utilizador.profile_img = imagem
        utilizador.save()
        user.save()
        return redirect('fotos:profile')

    return render(request, 'fotos/profile_edit.html')