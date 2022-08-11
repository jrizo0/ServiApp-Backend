# from django.db import models
# # from django.contrib import admin
#
# class Usuario(models.Model):
#     nombre_usuario = models.CharField(max_length=200)
#     apellido_usuario = models.CharField(max_length=200)
#     celular = models.CharField(max_length=200)
#     correo_electronico = models.CharField(max_length=200)
#     def __str__(self):
#         return self.correo_electronico
#
# class Domiciliario(models.Model):
#     usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
#     def __str__(self):
#         return self.usuario.correo_electronico
#
# class Cliente(models.Model):
#     usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
#     direccion = models.CharField(max_length=200)
#     def __str__(self):
#         return self.usuario.correo_electronico
#

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
# from django.db import models
#
#
# class Cliente(models.Model):
#     codcliente = models.SmallIntegerField(db_column='CODCLIENTE', primary_key=True)  # Field name made lowercase.
#     nombrecliente = models.CharField(db_column='NOMBRECLIENTE', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
#     direccion1 = models.CharField(db_column='DIRECCION1', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
#     e_mail = models.CharField(db_column='E_MAIL', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
#     tipo = models.SmallIntegerField(db_column='TIPO')  # Field name made lowercase.
#
#     class Meta:
#         managed = False
#         db_table = 'CLIENTE'
#
#
# class Tipocliente(models.Model):
#     idtipo = models.SmallIntegerField(db_column='IDTIPO', primary_key=True)  # Field name made lowercase.
#     descripcion = models.CharField(db_column='DESCRIPCION', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
#
#     class Meta:
#         managed = False
#         db_table = 'TIPOCLIENTE'
