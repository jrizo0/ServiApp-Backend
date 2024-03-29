from firebase_admin import firestore
from rest_framework import viewsets

import requests
import json
from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.serializers import ValidationError

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from ServiApp.firebase import db, fb_valid_req_token_uid, auth, dbrt
from django.conf import settings
from django.core.exceptions import PermissionDenied

from usuarios.views import UsuarioAPIView

API_Clientes = settings.SA_API_URL + "/clientes"
API_Tarifas = settings.SA_API_URL + "/tarifas"


class CartAPIView(viewsets.GenericViewSet):
    def retrieve(self, request):
        uid = self.request.query_params.get("uid")
        user_fs = db.collection("Usuario").document(uid).get()
        user_fs = user_fs.to_dict()
        if not user_fs["Carro"]:
            return Response({})
        cart_w_info = []
        for id_prod, item_cart_info in user_fs["Carro"].items():
            prod_info = db.collection("Producto").document(id_prod).get()
            if not prod_info.exists:
                continue
            prod_info = prod_info.to_dict()
            cart_w_info.append({"id": id_prod} | item_cart_info | prod_info)

        rest_info = (
            db.collection("Restaurante").document(user_fs["RestauranteCarro"]).get()
        )
        if not rest_info.exists:
            return Response("Error")
        rest_info = rest_info.to_dict()
        return Response(
            {
                "Domicilio": user_fs["DomicilioCarro"],
                "Restaurante": {"id": user_fs["RestauranteCarro"]} | rest_info,
                "Productos": cart_w_info,
            }
        )

    def add(self, request, id_prod, cant, id_rest, delivery):
        uid = self.request.query_params.get("uid")
        if cant == 0:
            return Response({"msg": "Cantidad es 0"})
        user = db.collection("Usuario").document(uid).get().to_dict()
        if user["DomicilioCarro"] != "" and user["DomicilioCarro"] != delivery:
            return Response(
                data={
                    "status": 302,
                    "msg": "No coincide la modalidad del pedido actual",
                },
            )

        id_rest_query_api = id_rest
        if "20-" in id_rest_query_api:
            id_rest_query_api = "20"
        price = requests.get(f"{API_Tarifas}/{id_rest_query_api}/{id_prod}/").json()[
            "precio"
        ]
        if user["RestauranteCarro"] != "" and id_rest != user["RestauranteCarro"]:
            return Response(
                status=status.HTTP_302_FOUND,
                data={
                    "status": 302,
                    "msg": "Ya tienes un pedido en proceso con otro restaurante",
                },
            )
        if user["RestauranteCarro"] == "":
            db.collection("Usuario").document(uid).update({"RestauranteCarro": id_rest})
        cart = user["Carro"]
        if not cart.get(id_prod):
            cart[id_prod] = {}
        cart[id_prod]["Precio"] = price
        cart[id_prod]["Cantidad"] = (
            cart[id_prod]["Cantidad"] + cant if cart[id_prod].get("Cantidad") else cant
        )
        db.collection("Usuario").document(uid).update(
            {"Carro": cart, "DomicilioCarro": delivery == 1}
        )
        return Response({"msg": "Producto añadido al carrito"})

    def remove(self, request, id_prod):
        uid = self.request.query_params.get("uid")
        user = db.collection("Usuario").document(uid).get().to_dict()
        cart = user["Carro"]
        cart.pop(id_prod)
        db.collection("Usuario").document(uid).update({"Carro": cart})
        if not cart:
            db.collection("Usuario").document(uid).update(
                {"RestauranteCarro": "", "DomicilioCarro": ""}
            )
        return Response({"msg": "Producto eliminado del carrito"})

    def clear(self, request):
        uid = self.request.query_params.get("uid")
        db.collection("Usuario").document(uid).update(
            {"RestauranteCarro": "", "Carro": {}, "DomicilioCarro": ""}
        )
        return Response({"msg": "Carrito vaciado"})

    def pay(self, request):
        # request.data = Carro:map, Domicilio:boolean, Estado, Fecha, Restaurante, Tarjeta
        uid = self.request.query_params.get("uid")
        user_info = UsuarioAPIView.get_queryset(UsuarioAPIView, uid)
        dt = datetime.now()
        cart = user_info["Carro"]
        for id_p in cart:
            prod = db.collection("Producto").document(id_p).get().to_dict()
            cart[id_p] = cart[id_p] | prod
        new_order = {
            "Usuario": uid,
            "UsuarioInfo": {
                "DeviceToken": user_info["DeviceToken"],
                "Telefono": user_info["Telefono"],
                "codcliente": user_info["codcliente"],
                "direccion1": user_info["direccion1"],
                "e_mail": user_info["e_mail"],
                "nombrecliente": user_info["nombrecliente"],
            },
            "Carro": cart,
            "Tarjeta": request.data["Tarjeta"],
            "Restaurante": user_info["RestauranteCarro"],
            "Domicilio": user_info["DomicilioCarro"],
            "Domiciliario": "",
            "Fecha": dt,
            "Total": request.data["Total"],
            "Direccion": request.data["Direccion"],
            "Finalizado": False,
            "Resena": {},
            # "Aceptado": False # Empieza sin este campo
        }
        fs_doc = db.collection("Orden").add(new_order)
        new_order = {"id": fs_doc[1].id} | new_order  # fs_doc: tuple (time, doc)
        orders_ref = dbrt.reference(f'Ordenes/{new_order["id"]}')
        rest = (
            db.collection("Restaurante")
            .document(user_info["RestauranteCarro"])
            .get()
            .to_dict()
        )
        dt_to_int = int(round(dt.timestamp()))
        orders_ref.set(
            {
                "NombreCliente": user_info["nombrecliente"],
                "RestauranteImagen": rest["Imagen"],
                "Total": request.data["Total"],
                "Domicilio": user_info["DomicilioCarro"],
                "Estado": -1,
                "IdRestaurante": user_info["RestauranteCarro"],
                "timestamp": dt_to_int,
            }
        )
        db.collection("Usuario").document(uid).update(
            {"RestauranteCarro": "", "Carro": {}, "DomicilioCarro": ""}
        )
        # TODO: guardar factura en serviciosalimentacion-api.
        return Response(new_order)
