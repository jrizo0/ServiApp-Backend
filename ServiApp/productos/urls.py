from django.urls import path

from . import views

app_name = 'productos'
urlpatterns = [
    path('get/', views.getProductos, name='getProductos'),
    path('get/<int:id>/', views.getProducto, name='getProducto'),
    path('create/', views.createProducto, name='createProducto'),
    path('update/<int:id>/', views.updateProducto, name='updateProducto'),
    path('delete/<int:id>/', views.deleteProducto, name='deleteProducto'),
]
