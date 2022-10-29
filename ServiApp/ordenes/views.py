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
        if not ord_fs.exists: 
            return Response({})
        ord_inf = ord_fs.to_dict()
        rest_inf = db.collection("Restaurante").document(ord_inf["Restaurante"]).get()
        if ord_fs.exists: 
            ord_inf["Restaurante"] = {"id": ord_inf["Restaurante"]} | rest_inf.to_dict()
        return ord_inf

    def retrieve(self, request):
        return Response(self.get_queryset())

    def list(self, request, role, delivery):
        # delivery = 0,1,2
        uid = self.request.query_params.get("uid")
        orders_fs = db.collection("Orden")
        res = []
        if delivery != 2:
            orders_fs = orders_fs.where("Domicilio", "==", delivery == 1)
        if role != "Domiciliario":
            orders_fs = orders_fs.where(role, "==", uid)
            orders_fs = orders_fs.get()
            for order in orders_fs:
                order_inf = order.to_dict()
                rest = (
                    db.collection("Restaurante")
                    .document(order_inf["Restaurante"])
                    .get()
                )
                if not rest.exists:
                    continue
                rest = rest.to_dict()
                order = {"id": order.id} | order_inf | {"Restaurante": rest}
                res.append(order)
        else:
            domiciliary = db.collection("Usuario").document(uid).get().to_dict()
            accepted_orders = domiciliary["DomiciliosAceptados"]
            for id_order in accepted_orders:
                order_inf = db.collection("Orden").document(id_order).get()
                if not order_inf.exists:
                    continue
                order_inf = order_inf.to_dict()
                rest = (
                    db.collection("Restaurante")
                    .document(order_inf["Restaurante"])
                    .get()
                )
                if not rest.exists:
                    continue
                rest = rest.to_dict()
                order = {"id": id_order} | order_inf | {"Restaurante": rest}
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

    def accept_order(self, request):
        uid = self.request.query_params.get("uid")
        user = db.collection("Usuario").document(uid)
        user_inf = user.get().to_dict()
        if user_inf["Rol"] == "Domiciliario":
            field_name = "DomiciliosAceptados"
            db.collection("Orden").document(request.data["id"]).update(
                {"Domiciliario": uid}
            )
        else:  # Restaurante
            field_name = "OrdenesAceptadas"
            db.collection("Orden").document(request.data["id"]).update(
                {"Aceptado": True}
            )
        if not field_name in user_inf:
            user.update({field_name: []})
        user.update({field_name: firestore.ArrayUnion([request.data["id"]])})
        return Response({"msg": f"Orden aceptada"})

    def reject_order(self, request):
        uid = self.request.query_params.get("uid")
        user = db.collection("Usuario").document(uid)
        user_inf = user.get().to_dict()
        if user_inf["Rol"] == "Domiciliario":
            field_name = "DomiciliosRechazados"
            db.collection("Orden").document(request.data["id"]).update(
                {"Domiciliario": uid}
            )
        else:  # Restaurante
            field_name = "OrdenesRechazadas"
            db.collection("Orden").document(request.data["id"]).update(
                {"Aceptado": False}
            )
        if not field_name in user_inf:
            user.update({field_name: []})
        user.update({field_name: firestore.ArrayUnion([request.data["id"]])})
        return Response({"msg": f"Orden rechazada"})

    def accepted_orders(self, request):
        uid = self.request.query_params.get("uid")
        user = db.collection("Usuario").document(uid)
        user_inf = user.get().to_dict()
        if user_inf["Rol"] == "Domiciliario":
            field_name = "DomiciliosAceptados"
        else:  # Restaurante
            field_name = "OrdenesAceptadas"
        if not field_name in user_inf:
            return Response([])
        user = db.collection("Usuario").document(uid).get().to_dict()
        return Response(user[field_name])

    def rejected_orders(self, request):
        uid = self.request.query_params.get("uid")
        user = db.collection("Usuario").document(uid)
        user_inf = user.get().to_dict()
        if user_inf["Rol"] == "Domiciliario":
            field_name = "DomiciliosRechazados"
        else:  # Restaurante
            field_name = "OrdenesRechazadas"
        if not field_name in user_inf:
            return Response([])
        user = db.collection("Usuario").document(uid).get().to_dict()
        return Response(user[field_name])
