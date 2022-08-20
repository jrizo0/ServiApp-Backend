from django.contrib import admin

from .models import Tarifav, Tarifa

class TarifavAdmin(admin.ModelAdmin):
    list_display = ('idtarifav', 'descripcion')
    list_filter = ['descripcion']
    search_fields = ['descripcion']

class TarifaAdmin(admin.ModelAdmin):
    list_display = ('idtarifav', 'descripcion', 'codarticulo', 'precio')
    list_filter = ['idtarifav']
    search_fields = ['idtarifav']

    def descripcion(self, obj):
        return obj.idtarifav.descripcion

admin.site.register(Tarifav, TarifavAdmin)
admin.site.register(Tarifa, TarifaAdmin)

