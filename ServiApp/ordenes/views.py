from rest_framework import viewsets

import requests

from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS, BasePermission

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from ServiApp.firebase import db, fb_valid_req_token
from django.conf import settings

from django.core.exceptions import PermissionDenied


API_Productos = settings.SA_API_URL + "/productos"
API_Tarifas = settings.SA_API_URL + "/tarifas"


class FBAuthenticated(BasePermission):
    def __init__(self):
        self.enable_auth = False

    def has_permission(self, request, view):
        return not self.enable_auth or fb_valid_req_token(request)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class OrdenesAPIView(viewsets.GenericViewSet):
    permission_classes = [ReadOnly | FBAuthenticated]

    def get_queryset(self):
        id = self.request.query_params.get("id")
        ord_fs = db.collection("Orden").document(id).get()
        return {"id": ord_fs.id} | ord_fs.to_dict()

    def list(self, request):
        ord_fs = db.collection("Orden").get()
        res = [{"id": e.id} | e.to_dict() for e in ord_fs]
        return Response(res)

    def retrieve(self, request):
        return Response(self.get_queryset())

    def update_status(self, request, status):
        id = self.request.query_params.get("id")
        db.collection("Orden").document(id).update({"Estado": status})
        return Response({"msg": "Estado de orden actualizado"})
        
        

