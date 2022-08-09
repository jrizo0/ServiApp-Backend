from django.db import models

from restaurantes.models import Restaurante

class Producto(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)
    nombre_producto = models.CharField(max_length=200)
    ingredientes = models.CharField(max_length=200)
    calorias = models.CharField(max_length=200)
    imagen = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=20, decimal_places=0)
    stock = models.DecimalField(max_digits=20, decimal_places=0)
    def __str__(self):
        return self.nombre_producto
