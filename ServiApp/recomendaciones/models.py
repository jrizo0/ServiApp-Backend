# from django.db import models

# class Ventas(models.Model):
#     transaccion = models.CharField(db_column='TRANSACCION', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     codarticulo = models.FloatField(db_column='CODARTICULO', blank=True, null=True)  # Field name made lowercase.
#     descripcion = models.CharField(db_column='DESCRIPCION', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     unidadestotal = models.FloatField(db_column='UNIDADESTOTAL', blank=True, null=True)  # Field name made lowercase.
#     precio = models.FloatField(db_column='PRECIO', blank=True, null=True)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'VENTAS'

# class Recomendaciones(models.Model):
#     antecedents = models.CharField(db_column='ANTECEDENTS', max_length=255, blank=True, null=True) 
#     consequents = models.CharField(db_column='CONSEQUENTS', max_length=255, blank=True, null=True) 
#     # antecedentsupport = models.CharField(db_column='ANTECEDENTSUPPORT', max_length=255, blank=True, null=True) 
#     # consequentsupport = models.CharField(db_column='CONSEQUENTSUPPORT', max_length=255, blank=True, null=True) 
#     # support = models.CharField(db_column='SUPPORT', max_length=255, blank=True, null=True) 
#     confidence = models.FloatField(db_column='CONFIDENCE', blank=True, null=True) 
#     # lift = models.FloatField(db_column='LIFT', blank=True, null=True) 
#     # leverage = models.FloatField(db_column='LEVERAGE', blank=True, null=True) 
#     # conviction = models.FloatField(db_column='CONVICTION', blank=True, null=True) 

#     class Meta:
#         managed = True
#         db_table = 'RECOMENDACIONES'
