from rest_framework import viewsets

import requests

# import json

from rest_framework.response import Response

# from django.core.cache import cache

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from ServiApp.firebase import db, fb_valid_req_token
from django.conf import settings
from django.core.exceptions import PermissionDenied, EmptyResultSet

API_Clientes = settings.SA_API_URL + "/clientes/"


class UsuarioAPIView(
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        # if not fb_valid_req_token(self.request):
        #     raise PermissionDenied()

        user_id = str(self.request.query_params.get("id"))
        try:
            res = db.collection("Usuario").document(user_id).get()
            if not res.exists:
                raise EmptyResultSet("EmptyResultSet exception with firebase user query")
        except EmptyResultSet as e:
            # return {"status": 400, "message": str(e)}
            return []
        return res.to_dict()

    # @method_decorator(vary_on_headers("Authorization"))
    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60 * 1))
    def retrieve(self, request):
        return Response(self.get_queryset())
