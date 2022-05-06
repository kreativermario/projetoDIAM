# Generated by Django 4.0.3 on 2022-04-27 18:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fotos', '0006_remove_foto_dislikes_remove_foto_users_reaction_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='foto',
            name='author',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
