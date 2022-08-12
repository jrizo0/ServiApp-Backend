from django.contrib import admin

from .models import Cliente

# admin.site.register(Cliente)

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('codcliente', 'nombrecliente', 'e_mail')
    # list_filter = ['nombrecliente']
    search_fields = ['nombrecliente']

admin.site.register(Cliente, ClienteAdmin)
