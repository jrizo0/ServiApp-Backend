from rest_framework import viewsets

from rest_framework.response import Response

from ServiApp.firebase import db
from django.conf import settings

from productos.views import retrieve_info, retrieve_info_deliv


API_Recomendaciones = settings.SA_API_URL + "/recomendaciones"
API_Ventas = settings.SA_API_URL + "/ventas"


class RecomendacionesAPIView(viewsets.GenericViewSet):
    def get_queryset(self, cart):
        prods = [int(p["id"]) for p in cart["Productos"]]
        recommendations = (
            db.collection("Recomendaciones").where("antecedents", "==", prods).get()
        )
        if len(recommendations) == 0:
            return []
        rec = recommendations[0].to_dict()
        res = []
        for p in rec["consequents"]:
            if cart["Domicilio"]:
                prod = retrieve_info_deliv(str(p), cart["Restaurante"]["id"])
            else:
                prod = retrieve_info(str(p), cart["Restaurante"]["id"])
            if prod != {}:
                res.append(prod)
            # res.append(str(p))
        return res

    # @method_decorator(vary_on_headers("Authorization"))
    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60 * 1))
    def retrieve(self, request):
        cart = request.data
        return Response(self.get_queryset(cart))
