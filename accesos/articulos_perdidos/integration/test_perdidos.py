# coding: utf-8

"""
Artículos Perdidos: registrar un artículo y consultarlo en Pendientes,
Entregados y Todos; entregarlo, donarlo o editarlo (articulos_perdidos.py:
nuevo_articulo, get_articles, update_article).
Notion: TB-146 a TB-150.
"""

import copy
import uuid

import pytest

from .fixtures import *
from .helpers import articulo_de_la_lista, payload_devolucion, payload_editar_articulo
from ..data.perdidos_data import (
    LOCATION,
    AREA,
    NOMBRE_ARTICULO,
    DEVOLUCION,
    DEVOLUCION_ENTREGADO,
    DEVOLUCION_DONADO,
    ESTATUS_PENDIENTE,
    ESTATUS_ENTREGADO,
    ESTATUS_DONADO,
    ESTATUS_TODOS,
    EDICION_COLOR,
    EDICION_DESCRIPCION,
)


@pytest.mark.integration
def test_registrar_articulo_lo_muestra_en_pendientes(mock_articulo_nuevo, articulo_pendiente):
    """
    TB-146: un artículo registrado desde + Nuevo Artículo debe aparecer en
    Pendientes con los datos que capturó el guardia. Si falta alguno, quien
    lo reclama no puede identificarlo.
    """
    assert articulo_pendiente.get("estatus_perdido") == ESTATUS_PENDIENTE, (
        f"El artículo quedó '{articulo_pendiente.get('estatus_perdido')}'"
    )
    assert articulo_pendiente.get("ubicacion_perdido") == LOCATION
    assert articulo_pendiente.get("area_perdido") == AREA
    for campo in ("tipo_articulo_perdido", "articulo_seleccion", "color_perdido", "descripcion", "date_hallazgo_perdido"):
        assert articulo_pendiente.get(campo) == mock_articulo_nuevo[campo], (
            f"'{campo}' quedó {articulo_pendiente.get(campo)!r}, se mandó {mock_articulo_nuevo[campo]!r}"
        )


@pytest.mark.integration
def test_entregar_articulo_lo_pasa_a_entregados(acceso_obj, articulo_pendiente):
    """
    TB-147: al entregar un artículo a su dueño debe quedar 'entregado', con
    fecha de entrega y los datos de quien lo recibe, aparecer en Entregados y
    salir de Pendientes. Si no, no queda constancia de a quién se entregó.
    """
    nombre = articulo_pendiente["articulo_perdido"]
    res = acceso_obj.update_article_lost(payload_devolucion(DEVOLUCION_ENTREGADO), articulo_pendiente["folio"])
    assert res.get("status_code") in (201, 202), f"No se pudo entregar el artículo: {res}"
    assert res["json"].get("date_entrega_perdido"), "El artículo entregado no tiene fecha de entrega"

    entregado = articulo_de_la_lista(acceso_obj, nombre, ESTATUS_ENTREGADO)
    assert entregado, "El artículo entregado no aparece en Entregados"
    assert entregado.get("recibe_perdido") == DEVOLUCION["recibe_perdido"]
    assert entregado.get("telefono_recibe_perdido") == DEVOLUCION["telefono_recibe_perdido"]
    assert articulo_de_la_lista(acceso_obj, nombre, ESTATUS_PENDIENTE) is None, "El artículo entregado sigue en Pendientes"


@pytest.mark.integration
def test_donar_articulo_lo_deja_donado_con_fecha(acceso_obj, articulo_pendiente):
    """
    TB-148: al donar un artículo (botón Donado, que manda 'Donado' con
    mayúscula) debe quedar 'donado', con fecha de entrega, y salir de
    Pendientes. Si no, el artículo donado sigue apareciendo como pendiente
    o sin fecha.
    """
    nombre = articulo_pendiente["articulo_perdido"]
    res = acceso_obj.update_article_lost(payload_devolucion(DEVOLUCION_DONADO), articulo_pendiente["folio"])
    assert res.get("status_code") in (201, 202), f"No se pudo donar el artículo: {res}"
    assert res["json"].get("date_entrega_perdido"), "El artículo donado no tiene fecha de entrega"

    donado = articulo_de_la_lista(acceso_obj, nombre, ESTATUS_TODOS)
    assert donado, "El artículo donado no aparece en Todos"
    assert donado.get("estatus_perdido") == ESTATUS_DONADO, f"El artículo donado quedó '{donado.get('estatus_perdido')}'"
    assert articulo_de_la_lista(acceso_obj, nombre, ESTATUS_PENDIENTE) is None, "El artículo donado sigue en Pendientes"


@pytest.mark.integration
def test_todos_trae_articulos_pendientes_y_entregados(acceso_obj, mock_articulo_nuevo, articulo_pendiente):
    """
    TB-150: la pestaña Todos no filtra por estatus. Con un artículo pendiente
    y otro entregado, Todos debe traer los dos, cada uno con su estatus; si
    falta uno, el historial de artículos queda incompleto.
    """
    otro = copy.deepcopy(mock_articulo_nuevo)
    otro["articulo_perdido"] = f"{NOMBRE_ARTICULO} {uuid.uuid4().hex[:8]}"
    res = acceso_obj.create_article_lost(otro)
    assert res.get("status_code") in (200, 201, 202), f"No se pudo registrar el segundo artículo: {res}"
    por_entregar = articulo_de_la_lista(acceso_obj, otro["articulo_perdido"], ESTATUS_PENDIENTE)
    assert por_entregar, "El segundo artículo no aparece en Pendientes"
    entrega = acceso_obj.update_article_lost(payload_devolucion(DEVOLUCION_ENTREGADO), por_entregar["folio"])
    assert entrega.get("status_code") in (201, 202), f"No se pudo entregar el segundo artículo: {entrega}"

    pendiente = articulo_de_la_lista(acceso_obj, articulo_pendiente["articulo_perdido"], ESTATUS_TODOS)
    entregado = articulo_de_la_lista(acceso_obj, otro["articulo_perdido"], ESTATUS_TODOS)
    assert pendiente, "El artículo pendiente no aparece en Todos"
    assert entregado, "El artículo entregado no aparece en Todos"
    assert pendiente.get("estatus_perdido") == ESTATUS_PENDIENTE
    assert entregado.get("estatus_perdido") == ESTATUS_ENTREGADO


@pytest.mark.integration
def test_editar_articulo_guarda_los_cambios(acceso_obj, articulo_pendiente):
    """
    TB-149: al editar un artículo y cambiar su color y descripción, la lista
    debe mostrar los valores nuevos con el mismo folio y el artículo seguir
    en Pendientes. Si no se guarda, quien lo reclama no lo reconoce.
    """
    cambios = {"color_perdido": EDICION_COLOR, "descripcion": EDICION_DESCRIPCION}
    res = acceso_obj.update_article_lost(payload_editar_articulo(articulo_pendiente, cambios), articulo_pendiente["folio"])
    assert res.get("status_code") in (201, 202), f"No se pudo editar el artículo: {res}"

    editado = articulo_de_la_lista(acceso_obj, articulo_pendiente["articulo_perdido"], ESTATUS_PENDIENTE)
    assert editado, "El artículo editado no sigue en Pendientes"
    assert editado["folio"] == articulo_pendiente["folio"], "La edición creó o modificó otro artículo"
    assert editado.get("color_perdido") == EDICION_COLOR, f"El color quedó {editado.get('color_perdido')!r}"
    assert editado.get("descripcion") == EDICION_DESCRIPCION, f"La descripción quedó {editado.get('descripcion')!r}"
