from django.shortcuts import get_object_or_404
from django import template

from fotos.models import Utilizador

register = template.Library()


@register.simple_tag(name="is_following")
def is_following(request_user_pk, user_pk):
    utilizador = get_object_or_404(Utilizador, user_id=user_pk)
    if utilizador.followers.filter(id=request_user_pk).exists():
        return True
    return False