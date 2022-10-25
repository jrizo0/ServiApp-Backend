from django.urls import path

from .views import CartAPIView

app_name = "carros"

retrieve_cart = CartAPIView.as_view({"get": "retrieve"})
add_prod_cart = CartAPIView.as_view({"post": "add"})
remove_prod_cart = CartAPIView.as_view({"post": "remove"})
clear_cart = CartAPIView.as_view({"post": "clear"})
pay_cart = CartAPIView.as_view({"post": "pay"})

urlpatterns = [
    path("", retrieve_cart),
    path("add/<str:id_prod>/<int:cant>/<str:id_rest>/<str:delivery>/", add_prod_cart),
    path("remove/<str:id_prod>/", remove_prod_cart),
    path("clear/", clear_cart),
    path("pay/", pay_cart),
]
