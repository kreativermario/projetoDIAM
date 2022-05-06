from django.urls import path
from . import views

app_name = 'fotos'
urlpatterns = [
    path('g', views.index, name='index'),
    path('', views.galeria, name='galeria'),
    path('foto/<str:pk>', views.verFoto, name='foto'),
    path('foto/<str:pk>/delete', views.removerFoto, name='eliminarFoto'),
    path('comunidade', views.comunidade, name='comunidade'),
    path('criar', views.criarFoto, name='criar'),
    path('registar', views.registar, name='registar'),
    path('login', views.user_login, name='login'),
    path('logout', views.process_logout, name='processlogout'),
    path('profile', views.profile, name='profile'),
    path('profile/edit', views.profile_edit, name='profile_edit'),
    path('foto/<str:pk>/comentario/', views.process_comentario, name='process_comentario'),

]