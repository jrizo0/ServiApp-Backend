from django.contrib import admin

from .models import Usuario, Domiciliario, Cliente

admin.site.register(Usuario)
admin.site.register(Domiciliario)
admin.site.register(Cliente)
