import django.urls
from django.views import View
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Categoria, Foto, Utilizador
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from .forms import RegisterForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

# Create your views here.


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


def galeria(request):
    categoria = request.GET.get('categoria')
    sort = request.GET.get('sort')
    url_parameter = request.GET.get('q')
    print(request.GET)
    if categoria is None:
        fotos = Foto.objects.all()
    else:
        # Aplicar filtro
        fotos = Foto.objects.filter(categoria__nome__contains=categoria)
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
    if url_parameter is not None:
        fotos = Foto.objects.filter(titulo__icontains=url_parameter)

    categorias = Categoria.objects.all()
    context = {
        'categorias': categorias,
        'fotos' : fotos
    }

    return render(request, 'fotos/galeria.html', context)


def verFoto(request, pk):
    foto = Foto.objects.get(id=pk)
    likes = foto.number_of_likes()
    is_allowed = is_member(request.user)
    liked = False
    if foto.likes.filter(id=request.user.id).exists():
        liked = True
    if request.method == 'POST':
        if request.POST.get('like') is not None:
            if foto.likes.filter(id=request.user.id).exists():
                liked = True
                context = {
                    'foto': foto,
                    'likes': likes,
                    'foto_is_liked': liked,
                    'is_allowed': is_allowed
                }
            else:
                foto.likes.add(request.user)
        if request.POST.get('dislike') is not None:
            if foto.likes.filter(id=request.user.id).exists():
                foto.likes.remove(request.user)
        # Fazer 'refresh' para a página anterior que era esta
        return redirect(request.META['HTTP_REFERER'])

    context = {
        'foto': foto,
        'likes': likes,
        'foto_is_liked': liked,
        'is_allowed': is_allowed
    }

    return render(request, 'fotos/foto.html', context)




def is_member(user):
    return user.groups.filter(name='utilizadores').exists()


@login_required(login_url=reverse_lazy('fotos:login'))
@user_passes_test(is_member, login_url=reverse_lazy('fotos:login'))
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
            author = request.user
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
                user =  User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['primeiro_nome'],
                    last_name=form.cleaned_data['ultimo_nome'],
                    password=form.cleaned_data['password']
                )
                utilizador = Utilizador(user=user)
                group = Group.objects.get(name='utilizadores')
                user.groups.add(group)
                utilizador.save()

                # Login the user
                login(request, user)

                return redirect('fotos:galeria')

    # No post data availabe, let's just show the page.
    else:
        form = RegisterForm()

    return render(request, template, {'form': form})


def user_login(request):
    if request.method == 'POST':
        # Process the request if posted data are available
        username = request.POST['username']
        password = request.POST['password']
        # Check username and password combination if correct
        user = authenticate(username=username, password=password)
        if user is not None:
            # Save session as cookie to login the user
            login(request, user)
            # Success, now let's login the user.
            return redirect('fotos:galeria')
        else:
            # Incorrect credentials, let's throw an error to the screen.
            return render(request, 'fotos/login.html', {'error_message': 'Username e/ou password incorretos!'})
    else:
        # No post data availabe, let's just show the page to the user.
        return render(request, 'fotos/login.html')




def process_logout(request):
        logout(request)
        return redirect('fotos:login')