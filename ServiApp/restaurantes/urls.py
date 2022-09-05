from django.urls import path

from .views import RestauranteAPIView

app_name = "restaurantes"

rest_list = RestauranteAPIView.as_view({"get": "list"})
rest_category = RestauranteAPIView.as_view({"get": "list_category"})

urlpatterns = [
    path("", rest_list),
    path("categoria/<int:id_category>/", rest_category),
]
