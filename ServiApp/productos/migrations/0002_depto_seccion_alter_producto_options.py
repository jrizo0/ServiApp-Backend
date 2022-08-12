# Generated by Django 4.0.6 on 2022-08-11 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Depto',
            fields=[
                ('numdpto', models.SmallIntegerField(db_column='NUMDPTO', primary_key=True, serialize=False)),
                ('descripcion', models.CharField(db_collation='Latin1_General_100_CS_AI_SC_UTF8', db_column='DESCRIPCION', max_length=50)),
            ],
            options={
                'db_table': 'DEPTO',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Seccion',
            fields=[
                ('numseccion', models.SmallIntegerField(db_column='NUMSECCION', primary_key=True, serialize=False)),
                ('descripcion', models.CharField(db_collation='Latin1_General_100_CS_AI_SC_UTF8', db_column='DESCRIPCION', max_length=50)),
            ],
            options={
                'db_table': 'SECCION',
                'managed': False,
            },
        ),
        migrations.AlterModelOptions(
            name='producto',
            options={'managed': False},
        ),
    ]