from django.urls import path
from . import views

app_name = 'fotos'
urlpatterns = [
    path('g', views.index, name='index'),
    path('', views.galeria, name='galeria'),
    path('foto/<str:pk>', views.verFoto, name='foto'),
    path('criar', views.criarFoto, name='criar'),
    path('registar', views.registar, name='registar'),
    path('login', views.user_login, name='login'),
    path('logout', views.process_logout, name='processlogout'),

]