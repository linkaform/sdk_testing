# coding: utf-8

"""
Fallas de Seguridad: crear una falla y consultarla en Abiertas, Cerradas y
Todos, cerrarla, editarla, agregarle seguimiento y eliminarla (fallas.py:
new_failure, get_failures, update_failure, update_failure_seguimiento,
delete_failure).
Notion: TB-138 a TB-143.
"""

import copy
import uuid

import pytest

from .fixtures import *
from .helpers import falla_de_la_lista, payload_editar_falla, payload_seguimiento
from ..data.fallas_data import (
    LOCATION,
    AREA,
    COMENTARIO_FALLA,
    COMENTARIO_EDITADO,
    ESTATUS_ABIERTO,
    ESTATUS_RESUELTO,
    ESTATUS_TODOS,
    CERRAR_FALLA,
    SEGUIMIENTO_FALLA,
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
@pytest.mark.bug(1521)
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


@pytest.mark.integration
@pytest.mark.bug(1521)
def test_todos_trae_fallas_abiertas_y_cerradas(acceso_obj, mock_falla_nueva, falla_abierta):
    """
    TB-143: la pestaña Todos no filtra por estatus. Con una falla abierta y
    otra cerrada, Todos debe traer las dos, cada una con su estatus; si falta
    una, el historial de fallas queda incompleto.
    """
    otra = copy.deepcopy(mock_falla_nueva)
    otra["falla_comentarios"] = f"{COMENTARIO_FALLA} {uuid.uuid4().hex[:8]}"
    res = acceso_obj.create_failure(otra)
    assert res.get("status_code") in (200, 201, 202), f"No se pudo crear la segunda falla: {res}"
    por_cerrar = falla_de_la_lista(acceso_obj, otra["falla_comentarios"], ESTATUS_ABIERTO)
    assert por_cerrar, "La segunda falla no aparece en Abiertas"
    cierre = acceso_obj.update_failure(dict(CERRAR_FALLA), por_cerrar["folio"])
    assert cierre.get("status_code") in (201, 202), f"No se pudo cerrar la segunda falla: {cierre}"

    abierta = falla_de_la_lista(acceso_obj, falla_abierta["falla_comentarios"], ESTATUS_TODOS)
    cerrada = falla_de_la_lista(acceso_obj, otra["falla_comentarios"], ESTATUS_TODOS)
    assert abierta, "La falla abierta no aparece en Todos"
    assert cerrada, "La falla cerrada no aparece en Todos"
    assert abierta.get("falla_estatus") == ESTATUS_ABIERTO
    assert cerrada.get("falla_estatus") == ESTATUS_RESUELTO


@pytest.mark.integration
def test_agregar_seguimiento_a_falla_lo_guarda(acceso_obj, falla_abierta):
    """
    TB-140: al agregar un seguimiento a una falla abierta sin cerrarla, la
    falla debe seguir abierta y mostrar ese seguimiento con su acción y su
    fecha. Si no se guarda, se pierde lo que ya se hizo para resolverla.
    """
    seguimiento = payload_seguimiento(falla_abierta)
    res = acceso_obj.update_failure_seguimiento(
        location="", area="", status=ESTATUS_ABIERTO, folio=falla_abierta["folio"], falla_grupo_seguimiento=seguimiento
    )
    assert res.get("status_code") in (201, 202), f"No se pudo agregar el seguimiento: {res}"

    falla = falla_de_la_lista(acceso_obj, falla_abierta["falla_comentarios"], ESTATUS_ABIERTO)
    assert falla, "La falla con seguimiento no sigue en Abiertas"
    seguimientos = falla.get("falla_grupo_seguimiento_formated") or []
    assert len(seguimientos) == 1, f"La falla tiene {len(seguimientos)} seguimientos, se agregó 1"
    assert seguimientos[0].get("falla_accion_realizada") == SEGUIMIENTO_FALLA["accion_correctiva_incidencia"], (
        f"La acción del seguimiento quedó {seguimientos[0].get('falla_accion_realizada')!r}"
    )
    assert seguimientos[0].get("falla_fecha_seguimiento") == seguimiento["fecha_inicio_seg"], (
        f"La fecha del seguimiento quedó {seguimientos[0].get('falla_fecha_seguimiento')!r}"
    )


@pytest.mark.integration
def test_eliminar_falla_la_quita_de_la_lista(acceso_obj, falla_abierta):
    """
    TB-142: al eliminar una falla desde la lista (delete-falla-modal manda la
    lista de folios), ya no debe aparecer en ninguna pestaña. Si sigue en
    Todos, la lista muestra fallas que el guardia ya borró.
    """
    res = acceso_obj.delete_failure([falla_abierta["folio"]])
    assert str(res.get("status_code")).startswith("2"), f"No se pudo eliminar la falla: {res}"

    assert falla_de_la_lista(acceso_obj, falla_abierta["falla_comentarios"], ESTATUS_TODOS) is None, (
        "La falla eliminada sigue en Todos"
    )
