# coding: utf-8

"""
Helpers de las pruebas de integración de Fallas.
"""

from ..data.fallas_data import LOCATION, FACET_COMENTARIOS, LIMITE_LISTA


def falla_de_la_lista(acceso_obj, comentario, status):
    """
    La falla con ese comentario en la lista (get_list_fallas como la pagina el
    front, con el comentario en el buscador), o None.
    """
    facets = [{"key": FACET_COMENTARIOS, "values": [comentario], "exact": False}]
    lista = acceso_obj.get_list_fallas([LOCATION], "", status=status, limit=LIMITE_LISTA, facets=facets)
    return next((f for f in lista["records"] if f.get("falla_comentarios") == comentario), None)
