from firebase_admin import firestore

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

from usuarios.views import UsuarioAPIView


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

    def retrieve(self, request):
        return Response(self.get_queryset())

    def list(self, request, role, delivery):
        # delivery = 0,1,2
        uid = self.request.query_params.get("uid")
        orders_fs = db.collection("Orden")
        if role == "Usuario":
            orders_fs = orders_fs.where("Usuario", "==", uid)
        if delivery == 0:
            orders_fs = orders_fs.where("Domicilio", "==", False)
        elif delivery == 1:
            orders_fs = orders_fs.where("Domicilio", "==", True)
        orders_fs = orders_fs.get()
        res = []
        for order in orders_fs:
            order_inf = order.to_dict()
            rest = db.collection("Restaurante").document(order_inf["Restaurante"]).get()
            if not rest.exists:
                continue
            rest = rest.to_dict()
            # for id_p in order_inf["Carro"]:
            #     prod = db.collection("Producto").document(id_p).get().to_dict()
            #     order_inf["Carro"][id_p] = order_inf["Carro"][id_p] | prod
            order = {"id": order.id} | order_inf | {"Restaurante": rest}
            if role == "Domiciliario" or role == "Restaurante":
                user = UsuarioAPIView.get_queryset(UsuarioAPIView, order_inf["Usuario"])
                order = order | {"Usuario": user}
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

    #Para domiciliarios
    def list_delivery(self, request):
        uid = self.request.query_params.get("uid")

        user = db.collection("Usuario").document(uid)
        if not "DomiciliosAceptados" in user.get().to_dict():
            user.update({"DomiciliosAceptados": []})
        if not "DomiciliosRechazados" in user.get().to_dict():
            user.update({"DomiciliosRechazados": []})

        rejected = db.collection("Usuario").document(uid).get()
        rejected = rejected.to_dict()["DomiciliosRechazados"]
        deliveries_fs = (
            db.collection("Orden")
            .where("Finalizado", "==", False)
            .where("Domicilio", "==", True)
            .get()
        )
        deliveries = []
        for delivery in deliveries_fs:
            if delivery.id in rejected:
                continue
            deliveries.append({"id": delivery.id} | delivery.to_dict())
        return Response(deliveries)
