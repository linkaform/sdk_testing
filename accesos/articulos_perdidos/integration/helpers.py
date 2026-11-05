# coding: utf-8

"""
Helpers de las pruebas de integración de Artículos Perdidos.
"""

from ..data.perdidos_data import LOCATION, FACET_NOMBRE, LIMITE_LISTA


def articulo_de_la_lista(acceso_obj, nombre, status):
    """
    El artículo con ese nombre en la lista (get_list_article_lost como la
    pagina el front, con el nombre en el buscador), o None.
    """
    facets = [{"key": FACET_NOMBRE, "values": [nombre], "exact": False}]
    lista = acceso_obj.get_list_article_lost(
        "", "", status, limit=LIMITE_LISTA, locations=[LOCATION], facets=facets
    )
    return next((a for a in lista["records"] if a.get("articulo_perdido") == nombre), None)
