from django.urls import path

from .views import UsersAPIView, RestaurantsAPIView, ProductsAPIView

app_name = "admin"

user_list = UsersAPIView.as_view({"get": "list"})
user_retrieve = UsersAPIView.as_view({"get": "retrieve"})
user_create_domiciliary = UsersAPIView.as_view({"post": "create_domiciliary"})
user_create_restaurant = UsersAPIView.as_view({"post": "create_restaurant"})
user_update = UsersAPIView.as_view({"put": "update"})
user_remove = UsersAPIView.as_view({"delete": "remove"})

rest_list = RestaurantsAPIView.as_view({"get": "list"})
rest_retrieve = RestaurantsAPIView.as_view({"get": "retrieve"})
rest_create = RestaurantsAPIView.as_view({"post": "create"})
rest_update = RestaurantsAPIView.as_view({"put": "update"})
rest_remove = RestaurantsAPIView.as_view({"delete": "remove"})

prod_list = ProductsAPIView.as_view({"get": "list"})
prod_retrieve = ProductsAPIView.as_view({"get": "retrieve"})
prod_create = ProductsAPIView.as_view({"post": "create"})
prod_update = ProductsAPIView.as_view({"put": "update"})
prod_remove = ProductsAPIView.as_view({"delete": "remove"})

urlpatterns = [
    path("usuarios/", user_list),
    path("usuarios/<str:uid>/", user_retrieve),
    path("usuarios/domiciliario/", user_create_domiciliary),
    path("usuarios/restaurante/", user_create_restaurant),
    path("usuarios/update/<str:uid>/", user_update),
    path("usuarios/remove/<str:uid>/", user_remove),

    path("restaurantes/", rest_list),
    path("restaurantes/<str:id>/", rest_retrieve),
    path("restaurantes/create/", rest_create),
    path("restaurantes/update/<str:id>/", rest_update),
    path("restaurantes/remove/<str:id>/", rest_remove),

    path("productos/", prod_list),
    path("productos/<str:id>/", prod_retrieve),
    path("productos/create/", prod_create),
    path("productos/update/<str:id>/", prod_update),
    path("productos/remove/<str:id>/", prod_remove),
]
