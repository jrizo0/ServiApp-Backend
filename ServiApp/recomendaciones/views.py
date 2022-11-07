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

API_Recomendaciones = settings.SA_API_URL + "/recomendaciones"
API_Ventas = settings.SA_API_URL + "/ventas"


class RecomendacionesAPIView(viewsets.GenericViewSet):

    def get_queryset(self, cart):
        recommendations = db.collection("Recomendacion").where("antecedents", "==", cart).get()
        if len(recommendations) == 0:
            return []
        res = recommendations[0].to_dict()
        return res

    # @method_decorator(vary_on_headers("Authorization"))
    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60 * 1))
    def retrieve(self, request):
        cart = request.data
        prods = [p["id"] for p in cart["Productos"]]
        return Response(self.get_queryset(prods))

