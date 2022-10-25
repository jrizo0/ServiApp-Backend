from django.urls import path, include
# from . import views

urlpatterns = [
    path('productos/', include('productos.urls')),
    path('restaurantes/', include('restaurantes.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('ordenes/', include('ordenes.urls')),
    path('carros/', include('carros.urls')),
]
