# Generated by Django 4.0.6 on 2022-07-29 01:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_usuario', models.CharField(max_length=200)),
                ('apellido_usuario', models.CharField(max_length=200)),
                ('celular', models.CharField(max_length=200)),
                ('correo_electronico', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Domiciliario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.usuario')),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direccion', models.CharField(max_length=200)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.usuario')),
            ],
        ),
    ]
