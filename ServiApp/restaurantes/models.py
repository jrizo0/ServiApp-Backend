from django.db import models

# class Tarifav(models.Model):
#     idtarifav = models.SmallIntegerField(db_column='IDTARIFAV', primary_key=True)  # Field name made lowercase.
#     descripcion = models.CharField(db_column='DESCRIPCION', max_length=50, db_collation='Latin1_General_100_CS_AI_SC_UTF8')  # Field name made lowercase.
#
#     class Meta:
#         managed = False
#         db_table = 'TARIFAV'
#
# class Tarifa(models.Model):
#     idtarifav = models.OneToOneField('Tarifav', models.DO_NOTHING, db_column='IDTARIFAV', primary_key=True)  # Field name made lowercase.
#     codarticulo = models.SmallIntegerField(db_column='CODARTICULO')  # Field name made lowercase.
#     precio = models.FloatField(db_column='PRECIO')  # Field name made lowercase.
#
#     class Meta:
#         managed = False
#         db_table = 'TARIFA'
#         unique_together = (('idtarifav', 'codarticulo'),)
#
#
