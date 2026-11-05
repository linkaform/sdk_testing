# coding: utf-8

"""
Fallas de Seguridad: crear una falla y consultarla en Abiertas, Cerradas y
Todos, cerrarla y editarla (fallas.py: new_failure, get_failures,
update_failure).
Notion: TB-138, TB-139 y TB-141.
"""

import uuid

import pytest

from .fixtures import *
from .helpers import falla_de_la_lista, payload_editar_falla
from ..data.fallas_data import (
    LOCATION,
    AREA,
    COMENTARIO_EDITADO,
    ESTATUS_ABIERTO,
    ESTATUS_RESUELTO,
    CERRAR_FALLA,
)


@pytest.mark.integration
def test_crear_falla_la_muestra_en_abiertas(mock_falla_nueva, falla_abierta):
    """
    TB-138: una falla creada desde + Nueva Falla debe aparecer en Abiertas
    con los datos que capturó el guardia. Si falta alguno, quien la atiende
    no sabe qué falló, dónde ni a quién le toca.
    """
    assert falla_abierta.get("falla_estatus") == ESTATUS_ABIERTO, f"La falla quedó '{falla_abierta.get('falla_estatus')}'"
    assert falla_abierta.get("falla_ubicacion") == LOCATION
    assert falla_abierta.get("falla_caseta") == AREA
    for campo in ("falla", "falla_objeto_afectado", "falla_reporta_nombre", "falla_responsable_solucionar_nombre", "falla_fecha_hora"):
        assert falla_abierta.get(campo) == mock_falla_nueva[campo], (
            f"'{campo}' quedó {falla_abierta.get(campo)!r}, se mandó {mock_falla_nueva[campo]!r}"
        )


@pytest.mark.integration
def test_cerrar_falla_la_pasa_a_cerradas(acceso_obj, falla_abierta):
    """
    TB-139: al cerrar una falla desde su detalle debe quedar 'resuelto' con
    fecha de solución, aparecer en Cerradas y salir de Abiertas. Si sigue en
    Abiertas, se vuelve a atender una falla que ya se resolvió.
    """
    comentario = falla_abierta["falla_comentarios"]
    res = acceso_obj.update_failure(dict(CERRAR_FALLA), falla_abierta["folio"])
    assert res.get("status_code") in (201, 202), f"No se pudo cerrar la falla: {res}"
    assert res["json"].get("falla_fecha_hora_solucion"), "La falla cerrada no tiene fecha de solución"

    cerrada = falla_de_la_lista(acceso_obj, comentario, ESTATUS_RESUELTO)
    assert cerrada, "La falla cerrada no aparece en Cerradas"
    assert falla_de_la_lista(acceso_obj, comentario, ESTATUS_ABIERTO) is None, "La falla cerrada sigue en Abiertas"


@pytest.mark.integration
def test_editar_falla_guarda_los_cambios(acceso_obj, falla_abierta):
    """
    TB-141: al editar una falla y cambiar sus comentarios, la lista debe
    mostrar el comentario nuevo y la falla seguir abierta. Si no se guarda,
    quien la atiende trabaja con la descripción vieja.
    """
    comentario_nuevo = f"{COMENTARIO_EDITADO} {uuid.uuid4().hex[:8]}"
    payload = payload_editar_falla(falla_abierta, {"falla_comentarios": comentario_nuevo})
    res = acceso_obj.update_failure(payload, falla_abierta["folio"])
    assert res.get("status_code") in (201, 202), f"No se pudo editar la falla: {res}"

    editada = falla_de_la_lista(acceso_obj, comentario_nuevo, ESTATUS_ABIERTO)
    assert editada, "La falla editada no aparece en Abiertas con el comentario nuevo"
    assert editada["folio"] == falla_abierta["folio"], "La edición creó o modificó otra falla"
