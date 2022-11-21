from datetime import datetime
import requests
from carros.views import CartAPIView
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from firebase_admin import firestore
from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.response import Response
from usuarios.views import UsuarioAPIView

from ServiApp.firebase import db, dbrt

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
            return {}
        ord_inf = {"id": ord_fs.id} | ord_fs.to_dict()
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
            orders_fs = orders_fs.where("Domiciliario", "==", delivery == 1)
        orders_fs = orders_fs.where(role, "==", uid)
        orders_fs = orders_fs.get()
        for order in orders_fs:
            order_inf = order.to_dict()
            rest = db.collection("Restaurante").document(order_inf["Restaurante"]).get()
            if not rest.exists:
                continue
            rest = {"id": rest.id} | rest.to_dict()
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

    def reorder(self, request):
        # uid = self.request.query_params.get("uid")
        # user = db.collection("Usuario").document(uid).get().to_dict()
        order_id = request.data["id"]
        order = db.collection("Orden").document(order_id).get()
        if not order.exists:
            return Response("No existe la orden")
        order = order.to_dict()
        # duplicar orden con otro id
        fs_doc = db.collection("Orden").add(order)
        order = {"id": fs_doc[1].id} | order  # fs_doc: tuple (time, doc)

        # campos de orden nueva
        dt = datetime.now()
        order ["Fecha"]: dt
        order["Resena"] = {}
        order["Direccion"] = request.data["Direccion"]
        order["Tarjeta"] = request.data["Tarjeta"]
        if "Aceptado" in order: 
            del order["Aceptado"]

        orders_ref = dbrt.reference(f'Ordenes/{order["id"]}')
        rest = (
            db.collection("Restaurante")
            .document(order["Restaurante"])
            .get()
            .to_dict()
        )
        dt_to_int = int(round(dt.timestamp()))
        orders_ref.set(
            {
                "NombreCliente": order["UsuarioInfo"]["nombrecliente"],
                "RestauranteImagen": rest["Imagen"],
                "Total": order["Total"],
                "Domicilio": order["Domicilio"],
                "Estado": -1,
                "IdRestaurante": order["Restaurante"],
                "timestamp": dt_to_int,
            }
        )
        # TODO: guardar factura en serviciosalimentacion-api.
        return Response(order)
