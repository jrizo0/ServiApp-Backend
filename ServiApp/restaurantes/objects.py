from types import SimpleNamespace as Namespace
import json
from json import JSONEncoder

class TarifavObject:
    def __init__(self, idtarifav, descripcion):
        self.idtarifav = idtarifav
        self.descripcion = descripcion

    class Meta:
        managed = False

class TarifaObject:
    def __init__(self, idtarifav, codarticulo, precio):
        self.idtarifav = idtarifav
        self.codarticulo = codarticulo
        self.precio = precio

class TarifavEncoder(JSONEncoder):
    def default(self, o): return o.__dict__

def TarifavDecoder(tarifav):
    tarifavJson = json.dumps(tarifav, indent=4, cls=TarifavDecoder)
    print(tarifavJson)
    return tarifavJson

def TarifavDecoder(tairfavJson):
    tarifav = json.loads(tairfavJson, object_hook=lambda d: Namespace(**d))
    print(tarifav)
    return tarifav
    
