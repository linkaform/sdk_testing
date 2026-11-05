# coding: utf-8

"""
Helpers de las pruebas de integración de Paquetería.
"""

from ..data.paqueteria_data import LOCATION, FACET_DESCRIPCION, LIMITE_LISTA


def paquete_de_la_lista(acceso_obj, descripcion, status):
    """
    El paquete con esa descripción en la lista (get_paquetes como la pagina el
    front, con la descripción en el buscador), o None.
    """
    facets = [{"key": FACET_DESCRIPCION, "values": [descripcion], "exact": False}]
    lista = acceso_obj.get_paquetes("", "", status, limit=LIMITE_LISTA, locations=[LOCATION], facets=facets)
    return next((p for p in lista["records"] if p.get("descripcion_paqueteria") == descripcion), None)
