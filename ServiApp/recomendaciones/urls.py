from django.urls import path

from .views import RecomendacionesAPIView

app_name = "recomendaciones"

get = RecomendacionesAPIView.as_view({"post": "retrieve"})

urlpatterns = [
    path("", get),
]
