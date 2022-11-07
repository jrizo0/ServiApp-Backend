# import requests
# import json
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from ServiApp.firebase import db

from django.conf import settings

API_Recomendaciones = settings.SA_API_URL + "/recomendaciones"


def schedule_api():
    print("Se envía recomendacion a usuarios")


def get_recomendaciones():
    ventas = pd.read_csv(
        # "https://www.dropbox.com/s/m1sfxzidetqwl6o/ventasDtServiApp.csv?dl=1",
        "https://www.dropbox.com/s/2yyzpcrzwk5zhgo/ventasDtServiApp3.csv?dl=1",
        sep=";",
        encoding="utf-8",
        decimal=".",
        # dtype={"Transaccion": "str", "CodArticulo": np.int32, "Descripcion": "str", "UnidadesTotal": np.int32, "Precio": np.float64}
        low_memory=False,
        # nrows=10,
    )
    my_basket = ventas.pivot_table(
        index="Transaccion",
        columns="CodArticulo",
        values="UnidadesTotales",
        aggfunc="sum",
    ).fillna(0)

    def encode(x):
        if x <= 0:
            return 0
        if x >= 1:
            return 1

    my_basket_sets = my_basket.applymap(encode)
    frequent_items = apriori(my_basket_sets, min_support=0.001, use_colnames=True)
    rules = association_rules(frequent_items, metric="lift", min_threshold=1)
    rules.sort_values("confidence", ascending=False, inplace=True)
    # print(rules)
    # print(len(rules))
    reset_fs(rules)


def reset_fs(data):
    docs = db.collection("Recomendaciones").get()
    for doc in docs:
        key = doc.id
        db.collection("Recomendaciones").document(key).delete()

    data = data.loc[:, ["antecedents", "consequents", "confidence"]].to_dict("index")
    for row in data.values():
        if row["confidence"] != 1:
            continue
        new_doc = {
            "antecedents": list(map(str, row["antecedents"])),
            "consequents": list(map(str, row["consequents"])),
            "confidence": row["confidence"],
        }
        # print(type(new_doc))
        db.collection("Recomendaciones").add(new_doc)
    print("...Updated recomendations...")
