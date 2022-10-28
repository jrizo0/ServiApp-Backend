from firebase_admin import firestore

from rest_framework import viewsets

import requests

from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS, BasePermission

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from ServiApp.firebase import db, dbrt
from django.conf import settings

from django.core.exceptions import PermissionDenied

from usuarios.views import UsuarioAPIView


API_Productos = settings.SA_API_URL + "/productos"
API_Tarifas = settings.SA_API_URL + "/tarifas"


class FBAuthenticated(BasePermission):
    def __init__(self):
        self.enable_auth = False

    # def has_permission(self, request, view):
    #     return not self.enable_auth or fb_valid_req_token(request)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class OrdenesAPIView(viewsets.GenericViewSet):
    permission_classes = [ReadOnly | FBAuthenticated]

    def get_queryset(self):
        id = self.request.query_params.get("id")
        ord_fs = db.collection("Orden").document(id).get()
        return {"id": ord_fs.id} | ord_fs.to_dict()

    def retrieve(self, request):
        return Response(self.get_queryset())

    def list(self, request, role, delivery):
        # delivery = 0,1,2
        uid = self.request.query_params.get("uid")
        orders_fs = db.collection("Orden")
        if delivery != 2:
            orders_fs = orders_fs.where("Domicilio", "==", delivery == 1)
        orders_exclude = []
        if role != "Domiciliario":
            orders_fs = orders_fs.where(role, "==", uid)
        else:
            domiciliary = db.collection("Usuario").document(uid).get().to_dict()
            orders_exclude = domiciliary["DomiciliosRechazados"]
        orders_fs = orders_fs.get()
        res = []
        for order in orders_fs:
            if order.id in orders_exclude:
                continue
            order_inf = order.to_dict()
            rest = db.collection("Restaurante").document(order_inf["Restaurante"]).get()
            if not rest.exists:
                continue
            rest = rest.to_dict()
            order = {"id": order.id} | order_inf | {"Restaurante": rest}
            res.append(order)
        res.sort(key=lambda r: r["Fecha"])
        res = res[::-1]
        return Response(res)

    def rate(self, request):
        uid = self.request.query_params.get("uid")
        doc = db.collection("Orden").document(request.data["id"])
        order = doc.get().to_dict()
        if order["Usuario"] != uid:
            return Response({"msg": f"El usuario no corresponde con el comprador"})
        doc.update({"Resena": request.data["Resena"]})
        return Response({"msg": f"Orden calificada"})

    def finish(self, request):
        doc = db.collection("Orden").document(request.data["id"])
        doc.update({"Finalizado": True})
        order_rt = dbrt.reference(f'Ordenes/{request.data["id"]}')
        order_rt.delete()
        return Response({"msg": f"Orden finalizada"})

    def accept_delivery(self, request):
        uid = self.request.query_params.get("uid")
        user = db.collection("Usuario").document(uid)
        if not "DomiciliosAceptados" in user.get().to_dict():
            user.update({"DomiciliosAceptados": []})
        user.update({"DomiciliosAceptados": firestore.ArrayUnion([request.data["id"]])})
        db.collection("Orden").document(request.data["id"]).update(
            {"Domiciliario": uid}
        )
        return Response({"msg": f"Domicilio aceptado"})

    def reject_delivery(self, request):
        uid = self.request.query_params.get("uid")
        user = db.collection("Usuario").document(uid)
        if not "DomiciliosRechazados" in user.get().to_dict():
            user.update({"DomiciliosRechazados": []})
        user.update(
            {"DomiciliosRechazados": firestore.ArrayUnion([request.data["id"]])}
        )
        return Response({"msg": f"Domicilio rechazado"})
