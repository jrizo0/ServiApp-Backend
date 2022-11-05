# import requests
# import json


# def schedule_api():
#     print("Se envía recomendacion a usuarios")

import numpy as np 
import pandas as pd
import re as re
import seaborn as sns
# from mlxtend.frequent_patterns import apriori, association_rules

def recomendaciones():
    ventas = pd.read_csv("https://www.dropbox.com/s/m1sfxzidetqwl6o/ventasDtServiApp.csv?dl=1", sep=";", encoding = "utf-8", decimal=".")
    my_basket = ventas.pivot_table(index='Transaccion', columns='Descripcion', values='UnidadesTotal', aggfunc='sum').fillna(0)
    # print(my_basket)

    def encode(x):
        if x<=0:
            return 0
        if x>=1:
            return 1

    my_basket_sets = my_basket.applymap(encode)
    frequent_items = apriori(my_basket_sets, min_support = 0.001,use_colnames = True)

    rules = association_rules(frequent_items, metric = "lift", min_threshold = 1)
    rules.sort_values('confidence', ascending = False, inplace = True)
    print(rules)
