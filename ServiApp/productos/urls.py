from django.urls import path

from .views import ProductosAPIView

app_name = "productos"

list = ProductosAPIView.as_view({"get": "list"})
retrieve = ProductosAPIView.as_view({"get": "retrieve"})
list_rest = ProductosAPIView.as_view({"get": "list_rest"})

urlpatterns = [
    path("", list),
    path("<str:id_prod>/<str:id_rest>/", retrieve),
    path("rest/<str:id_rest>/", list_rest),
]
