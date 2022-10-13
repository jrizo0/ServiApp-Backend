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

from ServiApp.firebase import db, fb_valid_req_token_uid, auth
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
                "Restaurante": {"id": user_fs["RestauranteCarro"]}
                | rest_info.to_dict(),
                "Productos": cart_w_info,
            }
        )

    def add_prod_cart(self, request, id_prod, cant, id_rest):
        uid = self.request.query_params.get("uid")
        if cant == 0:
            return Response({"msg": "Cantidad es 0"})
        user = db.collection("Usuario").document(uid).get().to_dict()
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
        cart[id_prod] = {}  # elimina lo anterior
        cart[id_prod]["Precio"] = price * cant
        cart[id_prod]["Cantidad"] = cant
        # TODO: Definir.
        # suma cantidad a la anterior
        # cart[id_prod]["Cantidad"] = cart[id_prod]["Cantidad"] + cant if cart[id_prod]["Cantidad"] else cant
        db.collection("Usuario").document(uid).update({"Carro": cart})
        return Response({"msg": "Producto añadido al carrito"})

    def remove_prod_cart(self, request, id_prod):
        uid = self.request.query_params.get("uid")
        user = db.collection("Usuario").document(uid).get().to_dict()
        cart = user["Carro"]
        cart.pop(id_prod)
        db.collection("Usuario").document(uid).update({"Carro": cart})
        if not cart:
            db.collection("Usuario").document(uid).update({"RestauranteCarro": ""})
        return Response({"msg": "Producto eliminado del carrito"})

    def clear_cart(self, request):
        uid = self.request.query_params.get("uid")
        db.collection("Usuario").document(uid).update(
            {"RestauranteCarro": "", "Carro": {}}
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
            # 0 por defecto, el pedido no se ha confirmado?
            "Estado": 0,  # request.data["Estado"],
            "Fecha": dt,
            "Restaurante": request.data["Restaurante"],
            "Tarjeta": request.data["Tarjeta"],
        }
        fs_doc = db.collection("Ordenes").add(new_order)
        new_order["id"] = fs_doc[1].id  # fs_doc: tuple (time, doc)
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
