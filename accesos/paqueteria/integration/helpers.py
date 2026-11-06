# coding: utf-8

"""
Helpers de las pruebas de integración de Paquetería.
"""

from datetime import datetime

import pytz

from ..data.paqueteria_data import LOCATION, FACET_DESCRIPCION, LIMITE_LISTA, ENTREGADO_A, ESTATUS_ENTREGADO


def paquete_de_la_lista(acceso_obj, descripcion, status):
    """
    El paquete con esa descripción en la lista (get_paquetes como la pagina el
    front, con la descripción en el buscador), o None.
    """
    facets = [{"key": FACET_DESCRIPCION, "values": [descripcion], "exact": False}]
    lista = acceso_obj.get_paquetes("", "", status, limit=LIMITE_LISTA, locations=[LOCATION], facets=facets)
    return next((p for p in lista["records"] if p.get("descripcion_paqueteria") == descripcion), None)


def payload_entrega(acceso_obj):
    """Payload de entregar-paqueteria.tsx con la fecha de entrega de ahora en la zona del usuario."""
    return {
        "estatus_paqueteria": [ESTATUS_ENTREGADO],
        "fecha_entregado_paqueteria": datetime.now(pytz.timezone(acceso_obj.user["timezone"])).strftime("%Y-%m-%d %H:%M:%S"),
        "entregado_a_paqueteria": ENTREGADO_A,
    }
