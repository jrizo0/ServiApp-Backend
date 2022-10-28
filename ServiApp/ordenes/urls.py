from django.urls import path

from .views import OrdenesAPIView

app_name = "ordenes"

list = OrdenesAPIView.as_view({"get": "list"})
retrieve = OrdenesAPIView.as_view({"get": "retrieve"})

rate = OrdenesAPIView.as_view({"post": "rate"})
finish = OrdenesAPIView.as_view({"post": "finish"})

accept_delivery = OrdenesAPIView.as_view({"post": "accept_delivery"})
reject_delivery = OrdenesAPIView.as_view({"post": "reject_delivery"})

urlpatterns = [
    path("<str:role>/<int:delivery>/", list),
    path("get/", retrieve),

    path("rate/", rate),
    path("finish/", finish),

    path("acceptdelivery/", accept_delivery),
    path("rejectdelivery/", reject_delivery),
]
