# Generated by Django 4.0.3 on 2022-05-04 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fotos', '0021_utilizador_background_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utilizador',
            name='background_img',
            field=models.ImageField(blank=True, upload_to='profile/'),
        ),
    ]