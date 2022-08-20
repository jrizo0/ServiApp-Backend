from django.urls import path

from . import views

app_name = 'clientes'
urlpatterns = [
    path('get/', views.getClientes, name='getClientes'),
    path('get/<int:id>/', views.getCliente, name='getCliente'),
    path('create/', views.createCliente, name='createCliente'),
    path('update/<int:id>/', views.updateCliente, name='updateCliente'),
    path('delete/<int:id>/', views.deleteCliente, name='deleteCliente'),
]
