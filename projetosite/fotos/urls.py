from django.urls import path
from . import views

app_name = 'fotos'
urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('index/', views.index, name='index'),
    path('galeria/', views.galeria, name='galeria'),
    path('galeria/foto/<str:pk>', views.verFoto, name='foto'),
    path('galeria/foto/<str:pk>/delete', views.removerFoto, name='eliminarFoto'),
    path('galeria/comunidade', views.comunidade, name='comunidade'),
    path('criar', views.criarFoto, name='criar'),
    path('registar', views.registar, name='registar'),
    path('login', views.user_login, name='login'),
    path('logout', views.process_logout, name='processlogout'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('profile/<str:pk>/edit', views.profile_edit, name='profile_edit'),
    path('galeria/foto/<str:pk>/comentario/', views.process_comentario, name='process_comentario'),
    path('403', views.no_perms_page, name='no_perms_page'),

]