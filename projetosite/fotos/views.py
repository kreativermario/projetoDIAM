import os
from django.db.models import Q
import django.urls
from django.views import View
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Categoria, Foto, Utilizador, Comentario, Rating
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect, Http404
from .forms import RegisterForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test


DEFAULT_PROFILE_URL = '/static/images/profile/default.jpg'


##################         FUNCOES        ##############################

# View 403
def no_perms_page(request):
    return render(request, 'fotos/no_perms.html')


# Ver se tem permissões!
def is_member(user):
    return user.groups.filter(name='utilizadores').exists()


# Função para remover a foto de perfil anterior, não remove a default
def delete_profile_img(utilizador):
    if utilizador.image_url != DEFAULT_PROFILE_URL:
        utilizador.profile_img.delete()


def is_staff(user):
    return user.groups.filter(name='utilizadores_staff').exists()



########################################################################

def inicio(request):
    return render(request, 'fotos/inicio.html')


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
        'fotos': fotos
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


# Lista de utilizadores
def comunidade(request):
    # Filtro de pesquisa
    pesquisa = request.GET.get('q')

    if pesquisa is None:
        utilizadores = Utilizador.objects.all()
    # Filtro por pesquisa
    else:
        utilizadores = Utilizador.objects.filter(user__username__icontains=pesquisa)

    context = {
        'utilizadores': utilizadores,
    }

    return render(request, 'fotos/comunidade.html', context)


# View que elimina comentário
@login_required(login_url=reverse_lazy('fotos:login'))
@user_passes_test(is_member, login_url=reverse_lazy('fotos:no_perms_page'))
def process_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    foto_id = comentario.foto.id
    liked = False
    # Dar like ou dislike
    if request.method == 'POST':
        # Se o user já deu like
        if comentario.likes.filter(id=request.user.id).exists():
            liked = True
        if liked is False:
            comentario.likes.add(request.user.id)
        else:
            comentario.likes.remove(request.user.id)

        return redirect('fotos:foto', foto_id)
    # Caso não seja para dar like ou dislike, é para remover
    if comentario.autor == request.user or request.user.is_superuser\
            or is_staff(request.user):
        comentario.delete()

    return redirect('fotos:foto', foto_id)


# View que elimina a foto
@login_required(login_url=reverse_lazy('fotos:login'))
@user_passes_test(is_member, login_url=reverse_lazy('fotos:no_perms_page'))
def removerFoto(request, pk):
    foto = get_object_or_404(Foto, pk=pk)
    if foto.autor == request.user or request.user.is_superuser or is_staff(request.user):
        foto.imagem.delete()
        foto.delete()
        return redirect('fotos:galeria')
    # Fazer 'refresh' para a página anterior
    return redirect(request.META['HTTP_REFERER'])


# Detalhe da foto
def verFoto(request, pk):
    foto = get_object_or_404(Foto, pk=pk)
    comentarios = Comentario.objects.filter(foto_id=pk).order_by('-created_date')
    likes = foto.number_of_likes()
    is_autor = False
    liked = False

    # Verifica se o user é o autor da foto
    if foto.autor == request.user:
        is_autor = True

    # Se o user já deu like
    if foto.likes.filter(id=request.user.id).exists():
        liked = True

    # Se houver um like ou dislike
    if request.method == 'POST':

        # Moderador faz rating da foto, criar ou alterar
        if request.POST.get('rating') is not None and is_staff(request.user):
            if Rating.objects.filter(foto_id=pk).exists():
                rating = Rating.objects.get(foto_id=pk)
                rating.rating = request.POST.get('rating')
                rating.user_rater_id = request.user.id
            else:
                rating, created = Rating.objects.get_or_create(
                    rating=request.POST.get('rating'),
                    user_rater_id=request.user.id,
                    foto_id=pk
                )
            rating.save()

        # Dar like só se ainda não deu like
        if request.POST.get('like') is not None and liked is False:
            foto.likes.add(request.user)

        # Dar Dislike se já deu like
        if request.POST.get('dislike') is not None and liked is True:
            foto.likes.remove(request.user)

        # Submit de um comentário, este está protegido pois os
        # botões para submit não são mostrados para utilizadores sem permissão
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
        # Se for selecionado uma categoria existente
        if data['categoria'] != "none":
            categoria = Categoria.objects.get(id=data['categoria'])
        # Se for criado uma nova categoria, é utilizada essa
        elif data['novaCategoria'] != '':
            # Cria uma categoria se já não existir.
            # Se já existir, faz um get e coloca na variavel categoria
            categoria, created = Categoria.objects.get_or_create(nome=data['novaCategoria'])
        else:
            categoria = None

        foto = Foto.objects.create(
            categoria=categoria,
            titulo=titulo,
            descricao=descricao,
            imagem=imagem,
            autor=request.user
        )

        return redirect('fotos:galeria')

    context = {
        'categorias': categorias,
    }
    return render(request, 'fotos/criar.html', context)


def registar(request):
    template = 'fotos/registar.html'

    # Se alguém se registar
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

                return redirect('fotos:profile', user.id)

    # Processar o template
    else:
        form = RegisterForm()

    return render(request, template, {'form': form})


def user_login(request):
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        # Se estiver válido
        if user is not None:
            login(request, user)
            return redirect('fotos:galeria')
        # Inválido
        else:
            return render(request, 'fotos/login.html', {'error_message': 'Username e/ou password incorretos!'})

    else:
        return render(request, 'fotos/login.html')


@login_required(login_url=reverse_lazy('fotos:login'))
def process_logout(request):
    logout(request)
    return redirect('fotos:login')


def profile(request, pk):
    user_perfil = get_object_or_404(User, pk=pk)
    utilizador_perfil = get_object_or_404(Utilizador, user_id=user_perfil.id)
    likes_count = 0
    fotos = Foto.objects.all()
    fotos_autor = fotos.filter(autor=user_perfil.id)
    autor_count = fotos_autor.count()
    is_following = False
    utilizador_visitante = None
    if request.user.is_authenticated and request.user.is_superuser is False:
        utilizador_visitante = get_object_or_404(Utilizador, user_id=request.user.id)
    if utilizador_perfil.followers.filter(id=request.user.id).exists():
        is_following = True

    following_list = utilizador_perfil.following.all()

    if request.method == 'POST':

        if request.POST.get('follow') is not None and is_following is False \
                and utilizador_visitante is not None:
            utilizador_perfil.followers.add(request.user)
            utilizador_visitante.following.add(user_perfil)
            utilizador_perfil.save()
            return redirect(request.META['HTTP_REFERER'])

        if request.POST.get('unfollow') is not None and is_following is True \
                and utilizador_visitante is not None:
            utilizador_perfil.followers.remove(request.user)
            utilizador_visitante.following.remove(user_perfil)
            utilizador_perfil.save()
            return redirect(request.META['HTTP_REFERER'])

        if request.POST.get('eliminar') == 'eliminar':

            if request.user.id == user_perfil.id:
                process_logout(request)
            if request.user.is_superuser or request.user.id == user_perfil.id:
                delete_profile_img(utilizador_perfil)
                utilizador_perfil.delete()
                user_perfil.delete()
                return redirect('fotos:comunidade')

    for foto in fotos:
        likes_count += foto.likes.filter(id=user_perfil.id).count()

    context = {
        'utilizador': utilizador_perfil,
        'user': user_perfil,
        "fotos": fotos_autor,
        'likes_count': likes_count,
        'autor_count': autor_count,
        'is_following': is_following,
        'following_list': following_list,
    }

    return render(request, 'fotos/profile.html', context)


@login_required(login_url=reverse_lazy('fotos:login'))
def profile_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    utilizador = get_object_or_404(Utilizador, user_id=pk)

    if request.method == 'POST':
        data = request.POST
        user = request.user
        if request.user == utilizador.user:
            imagem = request.FILES.get('profile_img')
            primeiro_nome = data['primeiro_nome']
            ultimo_nome = data['ultimo_nome']
            about = data['sobre_mim']

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
            return redirect('fotos:profile', user.id)

    context = {
        'utilizador': utilizador,
        'user': user,
    }

    return render(request, 'fotos/profile_edit.html', context)


