from django.db import models

# class Restaurante(models.Model):
#     nombre = models.CharField(max_length=200)
#     descripcion = models.CharField(max_length=200)
#     telefono = models.CharField(max_length=12)
#     horario_apertura = models.TimeField('horario de apertura')
#     horario_cierre = models.TimeField('horario de cierre')
#     def __str__(self):
#         return self.nombre

class Tarifav(models.Model):
    idtarifav = models.SmallIntegerField(db_column='IDTARIFAV', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=50, db_collation='Latin1_General_100_CS_AI_SC_UTF8')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TARIFAV'

class Tarifa(models.Model):
    idtarifav = models.OneToOneField('Tarifav', models.DO_NOTHING, db_column='IDTARIFAV', primary_key=True)  # Field name made lowercase.
    codarticulo = models.SmallIntegerField(db_column='CODARTICULO')  # Field name made lowercase.
    precio = models.FloatField(db_column='PRECIO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TARIFA'
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['idtarifav', 'codarticulo'], name='unique_tarifav_articulo_combination'
        #     )
        # ]
        unique_together = (('idtarifav', 'codarticulo'),)


