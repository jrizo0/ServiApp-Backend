from django.urls import path, include
from . import views

urlpatterns = [
    path('productos/', include('productos.urls')),
    path('restaurantes/', include('restaurantes.urls')),
    path('clientes/', include('clientes.urls')),
]
