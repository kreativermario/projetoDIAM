# Generated by Django 4.0.3 on 2022-04-29 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fotos', '0011_alter_utilizador_profile_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utilizador',
            name='profile_img',
            field=models.ImageField(blank=True, default='/stock/default.jpg', null=True, upload_to='profiles'),
        ),
    ]
