from django.db import models

class Restaurante(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=12)
    horario_apertura = models.TimeField('horario de apertura')
    horario_cierre = models.TimeField('horario de cierre')
    def __str__(self):
        return self.nombre
