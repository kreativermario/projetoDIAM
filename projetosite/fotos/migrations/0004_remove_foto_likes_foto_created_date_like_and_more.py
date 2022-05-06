# Generated by Django 4.0.3 on 2022-04-27 16:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fotos', '0003_utilizador'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foto',
            name='likes',
        ),
        migrations.AddField(
            model_name='foto',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('foto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='fotos.foto')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='like',
            constraint=models.UniqueConstraint(fields=('user', 'foto'), name='unique_like'),
        ),
    ]
