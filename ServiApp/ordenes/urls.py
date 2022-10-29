from django.urls import path

from .views import OrdenesAPIView

app_name = "ordenes"

list = OrdenesAPIView.as_view({"get": "list"})
retrieve = OrdenesAPIView.as_view({"get": "retrieve"})

rate = OrdenesAPIView.as_view({"post": "rate"})
finish = OrdenesAPIView.as_view({"post": "finish"})

accept_order = OrdenesAPIView.as_view({"post": "accept_order"})
reject_order = OrdenesAPIView.as_view({"post": "reject_order"})
accepted_orders = OrdenesAPIView.as_view({"get": "accepted_orders"})
rejected_orders = OrdenesAPIView.as_view({"get": "rejected_orders"})

urlpatterns = [
    path("<str:role>/<int:delivery>/", list),
    path("get/", retrieve),

    path("rate/", rate),
    path("finish/", finish),

    path("accept/", accept_order),
    path("reject/", reject_order),
    path("accepted/", accepted_orders),
    path("rejected/", rejected_orders),
]
