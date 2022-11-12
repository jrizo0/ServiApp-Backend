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
API_Restaurantes = settings.SA_API_URL + "/restaurantes"
API_Aforo = settings.AFORO_API_URL + "/aforo"
API_Productos = settings.SA_API_URL + "/productos"


class UsersAPIView(viewsets.GenericViewSet):
    def get_queryset(self):
        docs = (
            db.collection("Usuario")
            .where("Rol", "in", ["Domiciliario", "Restaurante"])
            .get()
        )
        return [{"id": u.id} | u.to_dict() for u in docs]

    def list(self, request):
        return Response(self.get_queryset())

    def retrieve(self, request, uid):
        user = db.collection("Usuario").document(id).get()
        data = {"id": user.id} | user.to_dict()
        return Response(data)

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
        uid = self.request.query_params.get("id")
        user = db.collection("Usuario").document(uid).get()
        if not user.exists:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"msg": "Usuario no encontrado"},
            )
        new_info = {}
        if "nombrecliente" in request.data:
            new_info["nombrecliente"] = request.data["nombrecliente"]
        if "e_mail" in request.data:
            new_info["e_mail"] = request.data["e_mail"]
        if "DeviceToken" in request.data:
            new_info["DeviceToken"] = request.data["DeviceToken"]
        if "Rol" in request.data:
            new_info["Rol"] = request.data["Rol"]
        if "Telefono" in request.data:
            new_info["Telefono"] = request.data["Telefono"]
        if "Restaurante" in request.data:
            new_info["Restaurante"] = request.data["Restaurante"]
        db.collection("Usuario").document(uid).update(new_info)
        user = db.collection("Usuario").document(uid).get().to_dict()
        return Response(user)

    def remove(self, request, uid):
        user = db.collection("Usuario").document(uid).get()
        if not user.exists:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"msg": "Usuario no encontrado"},
            )
        db.collection("Usuario").document(uid).delete()
        return Response("Usuario eliminado")


class RestaurantsAPIView(viewsets.GenericViewSet):
    def get_queryset(self):
        docs = db.collection("Restaurante").get()
        return [{"id": r.id} | r.to_dict() for r in docs]

    def list(self, request):
        return Response(self.get_queryset())

    def retrieve(self, request, id):
        rest = db.collection("Restaurante").document(id).get()
        data = {"id": rest.id} | rest.to_dict()
        return Response(data)

    def create(self, request):
        info_api = {
            "idtarifav": request.data["id"],
            "descripcion": request.data["Nombre"],
        }
        # info_api = requests.post(f"{API_Restaurantes}/", json=info_api)
        # if not info_api.status_code in [201, 200]:
        #     raise ValidationError()
        info_fs = {
            "Nombre": request.data["Nombre"],
            "Categoria": request.data["Categoria"],
            "Descripcion": request.data["Descripcion"],
            "Estado": request.data["Estado"],
            "Horario": request.data["Horario"],
            "Imagen": request.data["Imagen"],
            "Localizacion": request.data["Localizacion"],
            "Telefono": request.data["Telefono"],
            "TiempoEntrega": request.data["TiempoEntrega"],
        }
        db.collection("Restaurante").document(str(request.data["id"])).set(info_fs)
        return Response(info_fs)

    def update(self, request, id):
        rest = db.collection("Restaurante").document(id).get()
        if not rest.exists:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"msg": "Restaurante no encontrado"},
            )
        new_info = {}
        if "Nombre" in request.data:
            new_info["Nombre"] = request.data["Nombre"]
        if "Categoria" in request.data:
            new_info["Categoria"] = request.data["Categoria"]
        if "Descripcion" in request.data:
            new_info["Descripcion"] = request.data["Descripcion"]
        if "Estado" in request.data:
            new_info["Estado"] = request.data["Estado"]
        if "Horario" in request.data:
            new_info["Horario"] = request.data["Horario"]
        if "Imagen" in request.data:
            new_info["Imagen"] = request.data["Imagen"]
        if "Localizacion" in request.data:
            new_info["Localizacion"] = request.data["Localizacion"]
        if "Telefono" in request.data:
            new_info["Telefono"] = request.data["Telefono"]
        if "TiempoEntrega" in request.data:
            new_info["TiempoEntrega"] = request.data["TiempoEntrega"]
        db.collection("Restaurante").document(id).update(new_info)
        rest = db.collection("Restaurante").document(id).get().to_dict()
        return Response(rest)

    def remove(self, request, id):
        rest = db.collection("Restaurante").document(id).get()
        if not rest.exists:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"msg": "Restaurante no encontrado"},
            )
        db.collection("Restaurante").document(id).delete()
        return Response("Restaurante eliminado")


class ProductsAPIView(viewsets.GenericViewSet):
    def get_queryset(self):
        docs = db.collection("Producto").get()
        return [{"id": r.id} | r.to_dict() for r in docs]

    def list(self, request):
        return Response(self.get_queryset())

    def retrieve(self, request, id):
        prod = db.collection("Producto").document(id).get()
        data = {"id": prod.id} | prod.to_dict()
        return Response(data)

    def create(self, request):
        info_api = {
            "codarticulo": request.data["id"],
            "descripcion": request.data["Nombre"],
            "dpto": request.data["dpto"],
            "seccion": request.data["seccion"],
        }
        # info_api = requests.post(f"{API_Productos}/", json=info_api)
        # if not info_api.status_code in [201, 200]:
            # raise ValidationError()
        info_fs = {
            "Nombre": request.data["Nombre"],
            "Categoria": request.data["Categoria"],
            "Descripcion": request.data["Descripcion"],
            "Imagen": request.data["Imagen"],
        }
        db.collection("Producto").document(str(request.data["id"])).set(info_fs)
        return Response(info_fs)

    def update(self, request, id):
        prod = db.collection("Producto").document(id).get()
        if not prod.exists:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"msg": "Producto no encontrado"},
            )
        new_info = {}
        if "Nombre" in request.data:
            new_info["Nombre"] = request.data["Nombre"]
        if "Categoria" in request.data:
            new_info["Categoria"] = request.data["Categoria"]
        if "Descripcion" in request.data:
            new_info["Descripcion"] = request.data["Descripcion"]
        if "Imagen" in request.data:
            new_info["Imagen"] = request.data["Imagen"]
        db.collection("Producto").document(id).update(new_info)
        prod = db.collection("Producto").document(id).get().to_dict()
        return Response(prod)

    def remove(self, request, id):
        prod = db.collection("Producto").document(id).get()
        if not prod.exists:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"msg": "Producto no encontrado"},
            )
        db.collection("Producto").document(id).delete()
        return Response("Producto eliminado")
