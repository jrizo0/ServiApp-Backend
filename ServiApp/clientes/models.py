from django.db import models

# Create your models here.
class Tipocliente(models.Model):
    idtipo = models.SmallIntegerField(db_column='IDTIPO', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=50, db_collation='Latin1_General_100_CS_AI_SC_UTF8')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TIPOCLIENTE'


class Cliente(models.Model):
    codcliente = models.SmallIntegerField(db_column='CODCLIENTE', primary_key=True)  # Field name made lowercase.
    nombrecliente = models.CharField(db_column='NOMBRECLIENTE', max_length=50, db_collation='Latin1_General_100_CS_AI_SC_UTF8')  # Field name made lowercase.
    direccion1 = models.CharField(db_column='DIRECCION1', max_length=50, db_collation='Latin1_General_100_CS_AI_SC_UTF8', blank=True, null=True)  # Field name made lowercase.
    e_mail = models.CharField(db_column='E_MAIL', max_length=50, db_collation='Latin1_General_100_CS_AI_SC_UTF8')  # Field name made lowercase.
    tipo = models.ForeignKey('Tipocliente', models.DO_NOTHING, db_column='TIPO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CLIENTE'

