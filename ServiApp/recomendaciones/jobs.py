# import requests
# import json
import numpy as np
import pandas as pd
import re as re
import seaborn as sns
from mlxtend.frequent_patterns import apriori, association_rules
from ServiApp.firebase import db

from django.conf import settings

API_Recomendaciones = settings.SA_API_URL + "/recomendaciones"


def schedule_api():
    print("Se envía recomendacion a usuarios")


def get_recomendaciones():
    ventas = pd.read_csv(
        "https://www.dropbox.com/s/m1sfxzidetqwl6o/ventasDtServiApp.csv?dl=1",
        # "https://www.dropbox.com/s/evjiv3rw2he3epl/ventasDetalladasPorMeses.csv?dl=1",
        sep=";",
        encoding="utf-8",
        decimal=".",
        # dtype={"Transaccion": "str", "CodArticulo": np.int32, "Descripcion": "str", "UnidadesTotal": np.int32, "Precio": np.float64}
        low_memory=False,
        nrows=10,
    )
    my_basket = ventas.pivot_table(
        index="Transaccion",
        columns="Descripcion",
        values="UnidadesTotal",
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
    print(rules)
    reset_data(rules)

    # rule2 = rules.loc[[2], ["antecedents", "consequents", "confidence"]].to_dict('index')[2]
    # rule2b = {
    #     'antecedents': list(rule2['antecedents']),
    #     'consequents': list(rule2['consequents']),
    #     'confidence': rule2['confidence']
    # }
    # print(rule2b)


# TODO:
def reset_data(data):
    docs = db.collection("Recomendaciones").get()
    for doc in docs:
        key = doc.id
        db.collection("Recomendaciones").document(key).delete()

    data = data.loc[["antecedents", "consequents", "confidence"]].to_dict('index')
    for row in data.values():
        new_doc = {
            'antecedents': list(row['antecedents']),
            'consequents': list(row['consequents']),
            'confidence': row['confidence']
        }
        db.collection("Recomendaciones").add(new_doc)
