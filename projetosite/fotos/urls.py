from django.urls import path
from . import views

urlpatterns = [
    path('', views.galeria, name='galeria'),
    path('foto/<str:pk>', views.verFoto, name='foto'),
    path('criar', views.criarFoto, name='criar'),

]