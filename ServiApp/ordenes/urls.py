from django.urls import path

from .views import OrdenesAPIView

app_name = "ordenes"

list = OrdenesAPIView.as_view({"get": "list"})
retrieve = OrdenesAPIView.as_view({"get": "retrieve"})
update_status = OrdenesAPIView.as_view({"put": "update_status"})

urlpatterns = [
    path("", list),
    path("get/", retrieve),
    path("update/<str:status>/", update_status),
]
