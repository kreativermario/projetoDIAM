from django.shortcuts import get_object_or_404
from django import template

from fotos.models import Utilizador, Comentario

register = template.Library()


@register.simple_tag(name="is_following")
def is_following(request_user_pk, user_pk):
    utilizador = get_object_or_404(Utilizador, user_id=user_pk)
    if utilizador.followers.filter(id=request_user_pk).exists():
        return True
    return False


@register.simple_tag(name="is_liked")
def is_liked(request_user_id, comentario_pk):
    comentario = get_object_or_404(Comentario, pk=comentario_pk)
    if comentario.likes.filter(id=request_user_id).exists():
        return True
    return False


@register.simple_tag(name="is_member")
# Ver se tem permissões!
def is_member(user):
    return user.groups.filter(name='utilizadores').exists()


@register.simple_tag(name="is_staff")
def is_staff(user):
    return user.groups.filter(name='utilizadores_staff').exists()
