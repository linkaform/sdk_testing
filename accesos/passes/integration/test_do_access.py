# coding: utf-8

import copy
import pytest
from datetime import datetime
from pytz import timezone

from .fixtures import *
from .data.do_access_data import DIAS_SEMANA
from .helpers import (
    fecha_str,
    crear_pase,
    completar_pase_activo,
    cancelar_pase,
    obtener_qr_hijos,
    hacer_salida,
)


@pytest.mark.integration
def test_do_access_pase_en_proceso_no_permite_acceso(acceso_obj, mock_pase_do_access):
    """
    Un pase recién creado (sin foto/identificación) queda en estatus 'proceso'.
    do_access debe rechazarlo: si no, se dejaría entrar gente sin haber
    completado los requisitos de acceso.
    """
    folio = crear_pase(acceso_obj, mock_pase_do_access)
    with pytest.raises(Exception) as exc_info:
        acceso_obj.do_access(folio, DO_ACCESS_LOCATION, DO_ACCESS_AREA, {})
    assert "no se ha sido completado" in str(exc_info.value)


@pytest.mark.integration
@pytest.mark.prod_test
def test_do_access_pase_activo_permite_acceso(acceso_obj, mock_pase_do_access):
    """
    Un pase completado (foto + identificación + visita_a) llega a 'activo'
    y do_access debe crear el registro de entrada en BITACORA_ACCESOS.
    """
    folio = crear_pase(acceso_obj, mock_pase_do_access)
    completar_pase_activo(acceso_obj, folio)

    res = acceso_obj.do_access(folio, DO_ACCESS_LOCATION, DO_ACCESS_AREA, {})
    assert res.get('status_code') in (200, 201, 202)

    hacer_salida(acceso_obj, folio, DO_ACCESS_LOCATION, DO_ACCESS_AREA)


@pytest.mark.integration
def test_do_access_limite_de_entradas_excedido(acceso_obj, mock_pase_do_access):
    """
    Con config_limitar_acceso=1, la primera entrada+salida debe funcionar y
    la segunda entrada debe rechazarse por límite alcanzado. Sin este control
    un pase de una sola entrada podría reutilizarse indefinidamente.
    """
    pase = copy.deepcopy(mock_pase_do_access)
    pase["config_limitar_acceso"] = 1
    folio = crear_pase(acceso_obj, pase)
    completar_pase_activo(acceso_obj, folio)

    res_1 = acceso_obj.do_access(folio, DO_ACCESS_LOCATION, DO_ACCESS_AREA, {})
    assert res_1.get('status_code') in (200, 201, 202)
    hacer_salida(acceso_obj, folio, DO_ACCESS_LOCATION, DO_ACCESS_AREA)

    with pytest.raises(Exception) as exc_info:
        acceso_obj.do_access(folio, DO_ACCESS_LOCATION, DO_ACCESS_AREA, {})
    assert "limite de entradas" in str(exc_info.value)


@pytest.mark.integration
def test_do_access_dia_no_permitido(acceso_obj, mock_pase_do_access):
    """
    Si el pase solo permite acceso en un día distinto al actual, do_access
    debe rechazar la entrada aunque el pase esté activo y vigente.
    """
    hoy_idx = datetime.now(timezone('America/Mexico_City')).weekday()
    dia_no_hoy = DIAS_SEMANA[(hoy_idx + 1) % 7]

    pase = copy.deepcopy(mock_pase_do_access)
    pase["config_dias_acceso"] = [dia_no_hoy]
    folio = crear_pase(acceso_obj, pase)
    completar_pase_activo(acceso_obj, folio)

    with pytest.raises(Exception) as exc_info:
        acceso_obj.do_access(folio, DO_ACCESS_LOCATION, DO_ACCESS_AREA, {})
    assert "no te permite ingresar hoy" in str(exc_info.value)


@pytest.mark.integration
def test_do_access_ubicacion_no_valida(acceso_obj, mock_pase_do_access):
    """
    do_access debe rechazar el acceso si la ubicación enviada no está
    habilitada en el pase, sin importar que el pase esté activo y vigente.
    """
    folio = crear_pase(acceso_obj, mock_pase_do_access)
    completar_pase_activo(acceso_obj, folio)

    with pytest.raises(Exception) as exc_info:
        acceso_obj.do_access(folio, "Ubicacion Que No Existe En El Pase", DO_ACCESS_AREA, {})
    assert "no se encuentra en el pase" in str(exc_info.value)


@pytest.mark.integration
def test_do_access_pase_vencido(acceso_obj, mock_pase_do_access):
    """
    Un pase cuya fecha_desde_hasta ya pasó queda en estatus 'vencido' y
    do_access debe rechazarlo, para evitar que un pase caduco se siga usando.
    """
    pase = copy.deepcopy(mock_pase_do_access)
    pase["fecha_desde_visita"] = fecha_str(-5)
    pase["fecha_desde_hasta"] = fecha_str(-1)
    folio = crear_pase(acceso_obj, pase)

    detalle = acceso_obj.get_detail_access_pass(folio)
    assert detalle.get('estatus') == 'vencido'

    with pytest.raises(Exception) as exc_info:
        acceso_obj.do_access(folio, DO_ACCESS_LOCATION, DO_ACCESS_AREA, {})
    assert "vencido" in str(exc_info.value)


@pytest.mark.integration
def test_do_access_pase_cancelado(acceso_obj, mock_pase_do_access):
    """
    Cancelar un pase debe bloquear el acceso incluso si ya estaba activo,
    ya que 'cancelado' es el único estatus que puede forzar un operador.
    """
    folio = crear_pase(acceso_obj, mock_pase_do_access)
    completar_pase_activo(acceso_obj, folio)
    cancelar_pase(acceso_obj, folio)

    with pytest.raises(Exception) as exc_info:
        acceso_obj.do_access(folio, DO_ACCESS_LOCATION, DO_ACCESS_AREA, {})
    assert "cancelado" in str(exc_info.value)


@pytest.mark.integration
def test_do_access_grupo_padre_e_hijos_activos(acceso_obj, mock_pase_do_access_grupo):
    """
    Un pase grupal (padre + 2 acompañantes) completado y activo debe permitir
    dar acceso a los 3 juntos en una sola llamada a do_access vía
    selected_passes.
    """
    folio_padre = crear_pase(acceso_obj, mock_pase_do_access_grupo)
    qr_hijos = obtener_qr_hijos(acceso_obj, folio_padre)
    assert len(qr_hijos) == 2

    completar_pase_activo(acceso_obj, folio_padre)
    for qr_hijo in qr_hijos:
        completar_pase_activo(acceso_obj, qr_hijo)

    resultado = acceso_obj.do_access(
        folio_padre, DO_ACCESS_LOCATION, DO_ACCESS_AREA,
        {"selected_passes": qr_hijos}
    )
    accesos = resultado["accesos"]
    assert len(accesos) == 3
    assert all(a["status"] == "success" for a in accesos)

    hacer_salida(acceso_obj, folio_padre, DO_ACCESS_LOCATION, DO_ACCESS_AREA)
    for qr_hijo in qr_hijos:
        hacer_salida(acceso_obj, qr_hijo, DO_ACCESS_LOCATION, DO_ACCESS_AREA)


@pytest.mark.integration
def test_do_access_grupo_acompanante_con_limite_excedido_se_omite(acceso_obj, mock_pase_do_access_grupo):
    """
    Si un acompañante del grupo ya agotó su propio límite de entradas debe
    quedar fuera del grupo (status 'error') sin bloquear al resto: el límite
    de acceso es individual por qr_code aunque el resto de las validaciones
    se comparta en el pase grupal.
    """
    pase = copy.deepcopy(mock_pase_do_access_grupo)
    pase["config_limitar_acceso"] = 1
    folio_padre = crear_pase(acceso_obj, pase)
    qr_hijos = obtener_qr_hijos(acceso_obj, folio_padre)
    qr_agotado, qr_disponible = qr_hijos[0], qr_hijos[1]

    completar_pase_activo(acceso_obj, folio_padre)
    for qr_hijo in qr_hijos:
        completar_pase_activo(acceso_obj, qr_hijo)

    # Agota el limite del primer acompañante con una entrada+salida previa
    acceso_obj.do_access(qr_agotado, DO_ACCESS_LOCATION, DO_ACCESS_AREA, {})
    hacer_salida(acceso_obj, qr_agotado, DO_ACCESS_LOCATION, DO_ACCESS_AREA)

    resultado = acceso_obj.do_access(
        folio_padre, DO_ACCESS_LOCATION, DO_ACCESS_AREA,
        {"selected_passes": qr_hijos}
    )
    accesos = {a["qr_code"]: a for a in resultado["accesos"]}
    assert accesos[qr_agotado]["status"] == "error"
    assert accesos[qr_disponible]["status"] == "success"
    assert accesos[folio_padre]["status"] == "success"

    hacer_salida(acceso_obj, folio_padre, DO_ACCESS_LOCATION, DO_ACCESS_AREA)
    hacer_salida(acceso_obj, qr_disponible, DO_ACCESS_LOCATION, DO_ACCESS_AREA)
