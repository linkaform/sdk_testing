# coding: utf-8

"""
Paquetería: recibir un paquete y consultarlo en Pendientes, Entregados y
Todos, entregarlo y editarlo (paqueteria.py: nuevo_paquete, get_paquetes,
actualizar_paquete).
Notion: TB-152 a TB-156.
"""

import copy
import uuid

import pytest

from .fixtures import *
from .helpers import paquete_de_la_lista, payload_entrega, payload_editar_paquete
from ..data.paqueteria_data import (
    LOCATION,
    AREA,
    DESCRIPCION_PAQUETE,
    DESCRIPCION_EDITADA,
    DESTINATARIO_EXTERNO,
    ENTREGADO_A,
    ESTATUS_GUARDADO,
    ESTATUS_ENTREGADO,
    ESTATUS_TODOS,
)


@pytest.mark.integration
def test_recibir_paquete_para_empleado_lo_muestra_en_pendientes(mock_paquete_nuevo, paquete_guardado):
    """
    TB-152: un paquete recibido desde + Nuevo Paquete para un empleado debe
    aparecer en Pendientes con los datos que capturó el guardia. Si falta
    alguno, el destinatario no sabe que llegó ni dónde está guardado.
    """
    assert paquete_guardado.get("estatus_paqueteria") == ESTATUS_GUARDADO, (
        f"El paquete quedó '{paquete_guardado.get('estatus_paqueteria')}'"
    )
    assert paquete_guardado.get("ubicacion_paqueteria") == LOCATION
    assert paquete_guardado.get("area_paqueteria") == AREA
    for campo in ("quien_recibe_paqueteria", "proveedor", "guardado_en_paqueteria", "fecha_recibido_paqueteria"):
        assert paquete_guardado.get(campo) == mock_paquete_nuevo[campo], (
            f"'{campo}' quedó {paquete_guardado.get(campo)!r}, se mandó {mock_paquete_nuevo[campo]!r}"
        )


@pytest.mark.integration
def test_recibir_paquete_para_externo_lo_muestra_con_su_nombre(acceso_obj, mock_paquete_nuevo):
    """
    TB-153: un paquete para alguien que no es empleado (destinatario "Otro")
    debe aparecer en Pendientes con el nombre de esa persona como
    destinatario. Si sale vacío, el guardia no sabe a quién entregarlo.
    """
    paquete = copy.deepcopy(mock_paquete_nuevo)
    paquete.pop("quien_recibe_paqueteria")
    paquete["quien_recibe_otro"] = DESTINATARIO_EXTERNO
    res = acceso_obj.create_paquete(paquete)
    assert res.get("status_code") in (200, 201, 202), f"No se pudo recibir el paquete: {res}"

    guardado = paquete_de_la_lista(acceso_obj, paquete["descripcion_paqueteria"], ESTATUS_GUARDADO)
    assert guardado, "El paquete para el destinatario externo no aparece en Pendientes"
    assert guardado.get("quien_recibe_paqueteria") == DESTINATARIO_EXTERNO, (
        f"El destinatario quedó {guardado.get('quien_recibe_paqueteria')!r}"
    )


@pytest.mark.integration
def test_entregar_paquete_lo_pasa_a_entregados(acceso_obj, paquete_guardado):
    """
    TB-154: al entregar un paquete debe quedar 'entregado', con fecha de
    entrega y a quién se entregó, aparecer en Entregados y salir de
    Pendientes. Si sigue en Pendientes, el guardia lo busca en el locker
    aunque ya se lo llevaron.
    """
    descripcion = paquete_guardado["descripcion_paqueteria"]
    entrega = payload_entrega(acceso_obj)
    res = acceso_obj.update_paquete(entrega, paquete_guardado["folio"])
    assert res.get("status_code") in (201, 202), f"No se pudo entregar el paquete: {res}"

    entregado = paquete_de_la_lista(acceso_obj, descripcion, ESTATUS_ENTREGADO)
    assert entregado, "El paquete entregado no aparece en Entregados"
    assert entregado.get("fecha_entregado_paqueteria") == entrega["fecha_entregado_paqueteria"]
    assert entregado.get("entregado_a_paqueteria") == ENTREGADO_A
    assert paquete_de_la_lista(acceso_obj, descripcion, ESTATUS_GUARDADO) is None, "El paquete entregado sigue en Pendientes"


@pytest.mark.integration
def test_todos_trae_paquetes_guardados_y_entregados(acceso_obj, mock_paquete_nuevo, paquete_guardado):
    """
    TB-156: la pestaña Todos no filtra por estatus. Con un paquete guardado
    y otro entregado, Todos debe traer los dos, cada uno con su estatus; si
    falta uno, el historial de paquetería queda incompleto.
    """
    otro = copy.deepcopy(mock_paquete_nuevo)
    otro["descripcion_paqueteria"] = f"{DESCRIPCION_PAQUETE} {uuid.uuid4().hex[:8]}"
    res = acceso_obj.create_paquete(otro)
    assert res.get("status_code") in (200, 201, 202), f"No se pudo recibir el segundo paquete: {res}"
    por_entregar = paquete_de_la_lista(acceso_obj, otro["descripcion_paqueteria"], ESTATUS_GUARDADO)
    assert por_entregar, "El segundo paquete no aparece en Pendientes"
    entrega = acceso_obj.update_paquete(payload_entrega(acceso_obj), por_entregar["folio"])
    assert entrega.get("status_code") in (201, 202), f"No se pudo entregar el segundo paquete: {entrega}"

    guardado = paquete_de_la_lista(acceso_obj, paquete_guardado["descripcion_paqueteria"], ESTATUS_TODOS)
    entregado = paquete_de_la_lista(acceso_obj, otro["descripcion_paqueteria"], ESTATUS_TODOS)
    assert guardado, "El paquete guardado no aparece en Todos"
    assert entregado, "El paquete entregado no aparece en Todos"
    assert guardado.get("estatus_paqueteria") == ESTATUS_GUARDADO
    assert entregado.get("estatus_paqueteria") == ESTATUS_ENTREGADO


@pytest.mark.integration
def test_editar_paquete_guarda_cambios_y_conserva_area_y_destinatario(acceso_obj, paquete_guardado):
    """
    TB-155: al editar un paquete y cambiar su descripción, la lista debe
    mostrar la descripción nueva con el mismo folio y conservar el área y el
    destinatario. Si se pierden, el guardia no sabe dónde está ni de quién es.
    """
    descripcion_nueva = f"{DESCRIPCION_EDITADA} {uuid.uuid4().hex[:8]}"
    payload = payload_editar_paquete(paquete_guardado, {"descripcion_paqueteria": descripcion_nueva})
    res = acceso_obj.update_paquete(payload, paquete_guardado["folio"])
    assert res.get("status_code") in (201, 202), f"No se pudo editar el paquete: {res}"

    editado = paquete_de_la_lista(acceso_obj, descripcion_nueva, ESTATUS_GUARDADO)
    assert editado, "El paquete editado no aparece en Pendientes con la descripción nueva"
    assert editado["folio"] == paquete_guardado["folio"], "La edición creó o modificó otro paquete"
    assert editado.get("area_paqueteria") == paquete_guardado["area_paqueteria"], (
        f"El área quedó {editado.get('area_paqueteria')!r}, antes era {paquete_guardado['area_paqueteria']!r}"
    )
    assert editado.get("quien_recibe_paqueteria") == paquete_guardado["quien_recibe_paqueteria"], (
        f"El destinatario quedó {editado.get('quien_recibe_paqueteria')!r}, "
        f"antes era {paquete_guardado['quien_recibe_paqueteria']!r}"
    )
