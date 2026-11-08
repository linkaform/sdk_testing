# coding: utf-8

"""
Helpers de las pruebas de integración de Artículos Perdidos.
"""

import copy

from ..data.perdidos_data import LOCATION, FACET_NOMBRE, LIMITE_LISTA, DEVOLUCION


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


def payload_devolucion(estatus):
    """Payload de devolucion-article-modal con el tipo de devolución elegido."""
    payload = copy.deepcopy(DEVOLUCION)
    payload["estatus_perdido"] = estatus
    return payload


def payload_editar_articulo(articulo, cambios):
    """
    Payload de update_article_lost como lo arma editar-article-modal.tsx: los
    valores del artículo más los que el guardia cambió en el formulario.
    """
    payload = {
        "area_perdido": articulo.get("area_perdido") or "",
        "articulo_perdido": articulo.get("articulo_perdido") or "",
        "articulo_seleccion": articulo.get("articulo_seleccion") or "",
        "color_perdido": articulo.get("color_perdido") or "",
        "comentario_perdido": articulo.get("comentario_perdido") or "",
        "date_hallazgo_perdido": articulo.get("date_hallazgo_perdido") or "",
        "descripcion": articulo.get("descripcion") or "",
        "estatus_perdido": articulo.get("estatus_perdido") or "pendiente",
        "foto_perdido": articulo.get("foto_perdido") or [],
        "locker_perdido": articulo.get("locker_perdido") or "",
        "quien_entrega": articulo.get("quien_entrega") or "externo",
        "quien_entrega_externo": articulo.get("quien_entrega_externo") or "",
        "quien_entrega_interno": articulo.get("quien_entrega_interno") or "",
        "tipo_articulo_perdido": articulo.get("tipo_articulo_perdido") or "",
        "ubicacion_perdido": articulo.get("ubicacion_perdido") or "",
    }
    payload.update(cambios)
    return payload
