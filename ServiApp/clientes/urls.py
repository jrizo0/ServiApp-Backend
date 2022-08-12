from django.urls import path

from . import views

app_name = 'clientes'
urlpatterns = [
    path('get/', views.getClientes, name='getClientes'),
]
