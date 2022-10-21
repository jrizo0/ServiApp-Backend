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

API_Clientes = settings.SA_API_URL + "/clientes"
API_Tarifas = settings.SA_API_URL + "/tarifas"


class FBUserRequestAuthenticated(BasePermission):
    def __init__(self):
        self.enable_auth = False

    def has_permission(self, request, view):
        if self.enable_auth and not fb_valid_req_token_uid(request):
            raise PermissionDenied()
        return True


class UsuarioAPIView(viewsets.GenericViewSet):
    permission_classes = [FBUserRequestAuthenticated]

    def get_queryset(self):
        uid = self.request.query_params.get("uid")
        usu_api = requests.get(
            f"{API_Clientes}/{uid}/"
        )  # codcliente, nombre, direccion, email
        usu_fs = db.collection("Usuario").document(uid).get()  # telefono
        if usu_api.status_code != 200 or not usu_fs.exists:
            return []
        return usu_api.json() | usu_fs.to_dict()

    # @method_decorator(vary_on_headers("Authorization"))
    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60 * 1))
    def retrieve(self, request):
        return Response(self.get_queryset())

    def retrieve_cart(self, request):
        uid = self.request.query_params.get("uid")
        user_fs = db.collection("Usuario").document(uid).get()
        user_fs = user_fs.to_dict()
        if not user_fs["Carro"]:
            return Response({})
        cart_w_info = []
        for id_prod, item_cart_info in user_fs["Carro"].items():
            prod_info = db.collection("Producto").document(id_prod).get().to_dict()
            cart_w_info.append({"id": id_prod} | item_cart_info | prod_info)

        rest_info = (
            db.collection("Restaurante").document(user_fs["RestauranteCarro"]).get()
        )
        return Response(
            {
                "Domicilio": user_fs["DomicilioCarro"],
                "Restaurante": {"id": user_fs["RestauranteCarro"]}
                | rest_info.to_dict(),
                "Productos": cart_w_info,
            }
        )

    def add_prod_cart(self, request, id_prod, cant, id_rest, delivery):
        uid = self.request.query_params.get("uid")
        if cant == 0:
            return Response({"msg": "Cantidad es 0"})
        user = db.collection("Usuario").document(uid).get().to_dict()
        if user["DomicilioCarro"] != "" and user["DomicilioCarro"] != delivery:
            return Response({"msg": "No coincide modalidad de pedido"})

        id_rest_query_api = id_rest
        if "20-" in id_rest_query_api:
            id_rest_query_api = "20"
        price = requests.get(f"{API_Tarifas}/{id_rest_query_api}/{id_prod}/").json()[
            "precio"
        ]
        if user["RestauranteCarro"] != "" and id_rest != user["RestauranteCarro"]:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"msg": "Restaurante no coincide con el restaurante del carrito"},
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
            {"Carro": cart, "DomicilioCarro": delivery}
        )
        return Response({"msg": "Producto añadido al carrito"})

    def remove_prod_cart(self, request, id_prod):
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

    def clear_cart(self, request):
        uid = self.request.query_params.get("uid")
        db.collection("Usuario").document(uid).update(
            {"RestauranteCarro": "", "Carro": {}, "DomicilioCarro": ""}
        )
        return Response({"msg": "Carrito vaciado"})

    def pay_cart(self, request):
        # request.data = Carro:map, Domicilio:boolean, Estado, Fecha, Restaurante, Tarjeta
        uid = self.request.query_params.get("uid")
        user_fs = db.collection("Usuario").document(uid).get()
        user_fs = user_fs.to_dict()
        dt = datetime.now()
        new_order = {
            "Usuario": uid,
            "Carro": user_fs["Carro"],
            "Domicilio": request.data["Domicilio"],
            # "Estado": 0,
            "Fecha": dt,
            "Restaurante": user_fs["RestauranteCarro"],
            "Tarjeta": request.data["Tarjeta"],
            "Total": request.data["Total"],
            "Direccion": request.data["Direccion"],
        }
        fs_doc = db.collection("Orden").add(new_order)
        new_order = {"id": fs_doc[1].id} | new_order  # fs_doc: tuple (time, doc)
        orders_ref = dbrt.reference(f'ordenes/{new_order["id"]}')
        orders_ref.set({"estado": -1})
        db.collection("Usuario").document(uid).update(
            {"RestauranteCarro": "", "Carro": {}}
        )
        # TODO: guardar factura en serviciosalimentacion-api.
        return Response(new_order)

    def list_cards(self, request):
        uid = self.request.query_params.get("uid")
        cards = db.collection("Tarjeta").where("Usuario", "==", uid).get()
        return Response([{"id": card.id} | card.to_dict() for card in cards])

    def add_card(self, request):
        uid = self.request.query_params.get("uid")
        same_cards = (
            db.collection("Tarjeta")
            .where("Usuario", "==", uid)
            .where("NumeroTarjeta", "==", request.data["NumeroTarjeta"])
            .get()
        )
        if len(same_cards) > 0:
            return Response(
                exception=True,
                status=status.HTTP_400_BAD_REQUEST,
                data={"msg": "Tarjeta repetida"},
            )
        image = ""
        if request.data["Tipo"] == "Master Card":
            image = "https://storage.googleapis.com/serviapp-e9a34.appspot.com/Tarjeta/masterCard.png"
        elif request.data["Tipo"] == "American Express":
            image = "https://storage.googleapis.com/serviapp-e9a34.appspot.com/Tarjeta/american.jpg"
        elif request.data["Tipo"] == "Discover":
            image = "https://storage.googleapis.com/serviapp-e9a34.appspot.com/Tarjeta/discover.png"
        elif request.data["Tipo"] == "Visa":
            image = "https://storage.googleapis.com/serviapp-e9a34.appspot.com/Tarjeta/visa.png"
        db.collection("Tarjeta").add(
            {"Usuario": uid} | request.data | {"Imagen": image}
        )
        return Response({"msg": "Tarjeta añadida"})

    def delete_card(self, request):
        uid = self.request.query_params.get("uid")
        card_number = request.data["NumeroTarjeta"]
        q_cards = (
            db.collection("Tarjeta")
            .where("Usuario", "==", uid)
            .where("NumeroTarjeta", "==", card_number)
            .get()
        )
        if not q_cards:
            return Response(
                exception=True,
                status=status.HTTP_400_BAD_REQUEST,
                data={"msg": "Tarjeta no encontrada"},
            )
        for card in q_cards:
            db.collection("Tarjeta").document(card.id).delete()
        return Response({"msg": "Tarjeta eliminada"})

    def create(self, request):
        # {(api) nombrecliente, direccion1, e_mail, (auth) password, (fs) DeviceToken, Telefono}
        usu_form = request.data
        info_api = {
            "nombrecliente": usu_form["nombrecliente"],
            "direccion1": usu_form["direccion1"],
            "e_mail": usu_form["e_mail"],
            "tipo": 3,  # Por defecto usuario tipo estudiante
        }
        info_api = requests.post(f"{API_Clientes}/", json=info_api)
        if not info_api.status_code in [201, 200]:
            raise ValidationError()
        info_api = info_api.json()

        auth.create_user(
            uid=str(info_api["codcliente"]),
            email=info_api["e_mail"],
            password=usu_form["password"],
        )

        info_fs = {
            "DeviceToken": usu_form["DeviceToken"],
            "Rol": "Usuario",  # Por defecto rol usuario
            "RestauranteCarro": "",  # Por defecto vacio
            "DomicilioCarro": "",  # Por defecto vacio
            "Telefono": usu_form["Telefono"],
            "Carro": {},
        }
        db.collection("Usuario").document(str(info_api["codcliente"])).set(info_fs)

        return Response(info_api | {"Telefono": info_fs["Telefono"]})

    def update(self, request):
        if self.get_queryset() == []:  # Usuario no existe en fb
            raise ValidationError()
        uid = self.request.query_params.get("uid")
        # {(api) nombrecliente, direccion1, e_mail, (fs) Telefono}
        usu_form = request.data
        info_api = {
            "codcliente": int(uid),
            "nombrecliente": usu_form["nombrecliente"],
            "direccion1": usu_form["direccion1"],
            "e_mail": usu_form["e_mail"],
            "tipo": 3,  # Por defecto usuario tipo estudiante
        }
        info_api = requests.put(f"{API_Clientes}/{uid}/", json=info_api)
        if info_api.status_code in [201, 200]:  # Usuario no existe en api
            raise ValidationError()
        info_api = info_api.json()

        auth.update_user(
            uid=str(info_api["codcliente"]),
            email=info_api["e_mail"],
        )

        info_fs = {"Telefono": usu_form["Telefono"]}
        db.collection("Usuario").document(uid).update(
            {"Telefono": usu_form["Telefono"]}
        )

        return Response(info_api | {"Telefono": info_fs["Telefono"]})

    def change_pass(self, request):
        uid = self.request.query_params.get("uid")
        new_pass = str(request.data["new_pass"])
        user = auth.update_user(uid, password=new_pass)
        return Response(
            {"status": 200, "msg": f"Sucessfully updated pass to user: {user.uid}"}
        )

    def update_device_token(self, request):
        if self.get_queryset() == []:  # Usuario no existe en fb
            raise ValidationError()
        uid = self.request.query_params.get("uid")
        new_token = {"DeviceToken": request.data["DeviceToken"]}
        db.collection("Usuario").document(uid).update(new_token)
        return Response(
            {"status": 200, "msg": f"Sucessfully updated push token to user: {uid}"}
        )

    def list_orders(self, request, role, delivery):
        # delivery = 0,1,2
        uid = self.request.query_params.get("uid")
        orders_fs = db.collection("Orden")
        if uid != -1:
            orders_fs = orders_fs.where(role, "==", uid)
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
            for id_p in order_inf["Carro"]:
                prod = db.collection("Producto").document(id_p).get().to_dict()
                order_inf["Carro"][id_p] = order_inf["Carro"][id_p] | prod
            res.append({"id": order.id} | order_inf | {"Restaurante": rest})
        return Response(res)

    def rate_order(self, request):
        uid = self.request.query_params.get("uid")
        doc = db.collection("Orden").document(request.data["id"])
        order = doc.get().to_dict()
        if order["Usuario"] != uid:
            return Response({"msg": f"El usuario no corresponde con el comprador"})
        doc.update({"Reseña": request.data["Resena"]})
        return Response({"msg": f"Orden calificada"})
