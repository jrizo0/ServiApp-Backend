from django.urls import path

from .views import RestauranteAPIView

app_name = "restaurantes"

rest_list = RestauranteAPIView.as_view({"get": "list"})
rest_list_delivery = RestauranteAPIView.as_view({"get": "list_delivery"})
rest_aforo = RestauranteAPIView.as_view({"get": "aforo"})

urlpatterns = [
    path("", rest_list),
    path("domi/", rest_list_delivery),
    path("aforo/<str:id_rest>/", rest_aforo),
]
