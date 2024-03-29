# Generated by Django 4.0.3 on 2022-04-27 16:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fotos', '0004_remove_foto_likes_foto_created_date_like_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='foto',
            name='dislikes',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='foto',
            name='likes',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='foto',
            name='users_reaction',
            field=models.ManyToManyField(blank=True, related_name='reaction', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Like',
        ),
    ]
