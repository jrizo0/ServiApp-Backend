from django.urls import path

from .views import OrdenesAPIView

app_name = "ordenes"

list = OrdenesAPIView.as_view({"get": "list"})
retrieve = OrdenesAPIView.as_view({"get": "retrieve"})

rate = OrdenesAPIView.as_view({"post": "rate"})
finish = OrdenesAPIView.as_view({"post": "finish"})

accept_orders = OrdenesAPIView.as_view({"post": "accept_orders"})
reject_orders = OrdenesAPIView.as_view({"post": "reject_orders"})
accepted_orders = OrdenesAPIView.as_view({"get": "accepted_orders"})
rejected_orders = OrdenesAPIView.as_view({"get": "rejected_orders"})

urlpatterns = [
    path("<str:role>/<int:delivery>/", list),
    path("get/", retrieve),

    path("rate/", rate),
    path("finish/", finish),

    path("accept/", accept_orders),
    path("reject/", reject_orders),
    path("accepted/", accepted_orders),
    path("rejected/", rejected_orders),
]
