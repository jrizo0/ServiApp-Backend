from django.urls import path

from . import views

app_name = 'usuarios'
urlpatterns = [
    path('get/', views.getClientes, name='getClientes'),
]
