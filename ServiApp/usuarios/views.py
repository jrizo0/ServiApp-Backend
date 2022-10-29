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

    def get_queryset(self, uid):
        usu_api = requests.get(
            f"{API_Clientes}/{uid}/"
        )  # codcliente, nombre, direccion, email
        usu_fs = db.collection("Usuario").document(uid).get()  # telefono
        res = {}
        if usu_api.status_code == 200:
            res = res | usu_api.json()
        if usu_fs.exists:
            res = res | usu_fs.to_dict() 
        return res

    # @method_decorator(vary_on_headers("Authorization"))
    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60 * 1))
    def retrieve(self, request):
        uid = self.request.query_params.get("uid")
        return Response(self.get_queryset(uid))


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
            "Rol": "Usuario",
            "RestauranteCarro": "",  # Por defecto vacio
            "DomicilioCarro": "",  # Por defecto vacio
            "Telefono": usu_form["Telefono"],
            "Carro": {},
        }
        db.collection("Usuario").document(str(info_api["codcliente"])).set(info_fs)
        return Response(info_api | {"Telefono": info_fs["Telefono"]})

    def create_domiciliary(self, request):
        usu_form = request.data
        uid = auth.create_user(
            email=usu_form["e_mail"],
            password=usu_form["password"],
        ).uid
        info_fs = {
            "nombrecliente": usu_form["nombrecliente"],
            "e_mail": usu_form["e_mail"],
            "DeviceToken": usu_form["DeviceToken"],
            "Rol": "Domiciliario",
            "Telefono": usu_form["Telefono"],
            "DomiciliosAceptados": [],
            "DomiciliosRechazados": [],
        }
        db.collection("Usuario").document(uid).set(info_fs)
        return Response(info_fs)

    def create_restaurant(self, request):
        usu_form = request.data
        uid = auth.create_user(
            email=usu_form["e_mail"],
            password=usu_form["password"],
        ).uid
        info_fs = {
            "Restaurante": usu_form["Restaurante"],
            "nombrecliente": usu_form["nombrecliente"],
            "e_mail": usu_form["e_mail"],
            "DeviceToken": usu_form["DeviceToken"],
            "Rol": "Restaurante",
            "Telefono": usu_form["Telefono"],
            "OrdenesAceptadas": [],
            "OrdenesRechazados": [],
        }
        db.collection("Usuario").document(uid).set(info_fs)
        return Response(info_fs)

    def update(self, request):
        uid = self.request.query_params.get("uid")
        if self.get_queryset(uid) == []:  # Usuario no existe en fb
            raise ValidationError()
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
        uid = self.request.query_params.get("uid")
        if self.get_queryset(uid) == []:  # Usuario no existe en fb
            raise ValidationError()
        new_token = {"DeviceToken": request.data["DeviceToken"]}
        db.collection("Usuario").document(uid).update(new_token)
        return Response(
            {"status": 200, "msg": f"Sucessfully updated push token to user: {uid}"}
        )
