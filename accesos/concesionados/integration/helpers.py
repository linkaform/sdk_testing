# coding: utf-8

"""
Helpers de las pruebas de integración de Artículos Concesionados.
"""

from .data.concesiones_data import FACET_PERSONA, LIMITE_LISTA_CONCESIONES


def concesion_de_la_lista(acceso_obj, persona, location, area=""):
    """
    La concesión de esa persona en la lista (get_list_articulos_concesionados
    como la pagina el front, con la persona en el buscador), o None.
    """
    facets = [{"key": FACET_PERSONA, "values": [persona], "exact": False}]
    lista = acceso_obj.get_list_articulos_concesionados(
        location="", area=area, limit=LIMITE_LISTA_CONCESIONES, locations=[location], facets=facets
    )
    return next((c for c in lista["records"] if c.get("persona_nombre_otro") == persona), None)
