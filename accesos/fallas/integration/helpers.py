# coding: utf-8

"""
Helpers de las pruebas de integración de Fallas.
"""

import copy
from datetime import datetime, timedelta

from ..data.fallas_data import LOCATION, FACET_COMENTARIOS, LIMITE_LISTA, SEGUIMIENTO_FALLA, TIEMPO_SEGUIMIENTO


def falla_de_la_lista(acceso_obj, comentario, status):
    """
    La falla con ese comentario en la lista (get_list_fallas como la pagina el
    front, con el comentario en el buscador), o None.
    """
    facets = [{"key": FACET_COMENTARIOS, "values": [comentario], "exact": False}]
    lista = acceso_obj.get_list_fallas([LOCATION], "", status=status, limit=LIMITE_LISTA, facets=facets)
    return next((f for f in lista["records"] if f.get("falla_comentarios") == comentario), None)


def payload_editar_falla(falla, cambios):
    """
    Payload de update_failure como lo arma editar-falla.tsx: los valores de la
    falla más los que el guardia cambió en el formulario.
    """
    payload = {
        "falla": falla.get("falla") or "",
        "falla_caseta": falla.get("falla_caseta") or "",
        "falla_comentarios": falla.get("falla_comentarios") or "",
        "falla_documento": falla.get("falla_documento") or [],
        "falla_estatus": "abierto",
        "falla_evidencia": falla.get("falla_evidencia") or [],
        "falla_fecha_hora": falla.get("falla_fecha_hora") or "",
        "falla_objeto_afectado": falla.get("falla_objeto_afectado") or "",
        "falla_reporta_nombre": falla.get("falla_reporta_nombre") or "",
        "falla_responsable_solucionar_nombre": falla.get("falla_responsable_solucionar_nombre") or "",
        "falla_ubicacion": falla.get("falla_ubicacion") or "",
    }
    payload.update(cambios)
    return payload


def payload_seguimiento(falla):
    """
    Seguimiento de add-seguimiento-falla-cerrar.tsx una hora después de la
    falla, con el tiempo transcurrido como lo calcula el front.
    """
    inicio = datetime.strptime(falla["falla_fecha_hora"], "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)
    seguimiento = copy.deepcopy(SEGUIMIENTO_FALLA)
    seguimiento["fecha_inicio_seg"] = inicio.strftime("%Y-%m-%d %H:%M:%S")
    seguimiento["tiempo_transcurrido"] = TIEMPO_SEGUIMIENTO
    return seguimiento
