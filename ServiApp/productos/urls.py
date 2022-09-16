from django.urls import path

from .views import ProductosAPIView

app_name = "productos"

list = ProductosAPIView.as_view({"get": "list"})
list_category = ProductosAPIView.as_view({"get": "list_category"})
list_rest = ProductosAPIView.as_view({"get": "list_rest"})
list_rest_by_category = ProductosAPIView.as_view({"get": "list_rest_by_category"})

urlpatterns = [
    path("", list),
    path("category/<str:id_category>/", list_category),
    path("rest/<str:id_rest>/", list_rest),
    path("rest/<str:id_rest>/cat/", list_rest_by_category),
]
