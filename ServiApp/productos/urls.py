from django.urls import path

from . import views

app_name = 'productos'
urlpatterns = [
    path('get/', views.getProductos, name='getProductos'),
]
