"""Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS.

./lkf test corre SOLO este archivo cuando cambia alguna funcion de
C10_TRIGGERS. Aqui van los casos principales de cada funcion y las
validaciones mas importantes; los demas unitarios de la seccion viven en
otros archivos de unit/ y se corren a mano.
"""

import pytest
import json
import pytz
from ..data.nuevo_acceso_data import (
    LOCATION,
    AREAS_SIMULADAS,
    ANFITRIONES_SIMULADOS,
    AREA,
    QR_PASE_UNIT,
    PASE_DETALLE_ACTIVO,
    SIN_INGRESOS,
    DIAS_SEMANA,
    ZONA_DIA_ACCESO,
    LIMITE_ENTRADAS,
    INGRESOS_EN_EL_LIMITE,
    VENCIDO_HACE_MIN,
    DENTRO_DE_TOLERANCIA_MIN,
    ENTRADA_REGISTRADA,
    CITA_FUERA_DE_TOLERANCIA_MIN,
    VIGENTE_POR_MIN,
    CONFIG_SIN_TOLERANCIA,
    OTRA_UBICACION,
)
from datetime import datetime
from lkf_back import de
from .helpers import fecha_relativa

C10_TRIGGERS = [
    "assets_access_pass",
    "do_access",
]


# --- assets access pass ---
@pytest.mark.unit
@pytest.mark.bug(1482)
def test_assets_access_pass_sin_configuracion_no_truena(accesos_no_api, mocker):
    """
    TB-079: si falla la configuración de la ubicación, assets_access_pass
    debe regresar las áreas y los anfitriones con perfiles, requerimientos y
    envíos vacíos. Antes el except asignaba 'Perfiles' (con mayúscula) y el
    return usaba 'perfiles', lo que daba UnboundLocalError y el modal no cargaba.
    Bug 2610-1482 corregido (addons #31).
    """
    mocker.patch.object(de(accesos_no_api, "get_areas_by_location"), "get_areas_by_location", return_value=AREAS_SIMULADAS)
    mocker.patch.object(
        accesos_no_api.Employee, "get_users_by_location_area", return_value=ANFITRIONES_SIMULADOS
    )
    mocker.patch.object(
        accesos_no_api, "get_config_modulo_seguridad", side_effect=Exception("config no disponible")
    )

    assets = accesos_no_api.assets_access_pass(LOCATION)

    assert assets["Areas"] == AREAS_SIMULADAS
    assert assets["Visita_a"] == [a["name"] for a in ANFITRIONES_SIMULADOS]
    assert assets["Perfiles"] == []
    assert assets["requerimientos"] == []
    assert assets["envios"] == []


# --- do access estatus ---
@pytest.mark.unit
def test_pase_cancelado_no_da_acceso(accesos_no_api, mocker):
    """
    TB-173: un pase cancelado debe detenerse con el error de pase cancelado
    y no registrar la entrada. Si se registra, entra alguien cuyo pase ya
    se dio de baja.
    """
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value={**PASE_DETALLE_ACTIVO, "estatus": "cancelado"})
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="El pase esta cancelado"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()


@pytest.mark.unit
def test_pase_vencido_no_da_acceso(accesos_no_api, mocker):
    """
    TB-174: un pase vencido debe detenerse con el error de pase vencido y no
    registrar la entrada. Si se registra, entra alguien fuera de la vigencia
    que le dieron.
    """
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value={**PASE_DETALLE_ACTIVO, "estatus": "vencido"})
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="El pase esta vencido"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()


@pytest.mark.unit
def test_pase_que_llego_a_su_limite_de_entradas_no_da_acceso(accesos_no_api, mocker):
    """
    TB-177: un pase activo con límite de entradas que ya las usó todas debe
    detenerse con el aviso de límite completado y no registrar otra entrada.
    Si se registra, el pase da más entradas de las que se autorizaron.
    """
    mocker.patch.object(
        accesos_no_api, "get_detail_access_pass", return_value={**PASE_DETALLE_ACTIVO, "limite_de_acceso": LIMITE_ENTRADAS}
    )
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(INGRESOS_EN_EL_LIMITE))
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="limite de entradas"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()


# --- do access fechas ---
@pytest.mark.unit
def test_pase_con_mas_de_una_hora_de_vencido_no_da_acceso(accesos_no_api, mocker):
    """
    TB-178: un pase activo cuya fecha de caducidad pasó hace más de 1 hora
    (el margen de tolerancia) debe detenerse con el aviso de que ya pasó su
    vigencia y no registrar la entrada.
    """
    pase = {**PASE_DETALLE_ACTIVO, "fecha_de_caducidad": fecha_relativa(accesos_no_api, -VENCIDO_HACE_MIN)}
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value=pase)
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="ya paso su fecha de vigencia"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()


@pytest.mark.unit
def test_dentro_de_la_hora_de_tolerancia_el_pase_si_da_acceso(accesos_no_api, mocker):
    """
    TB-179: un pase activo que venció hace menos de 1 hora sigue dentro del
    margen de tolerancia: debe registrar la entrada en la ubicación y la
    caseta. Si lo rechaza, el visitante que llega un poco tarde no puede
    entrar aunque el margen se lo permite.
    """
    pase = {**PASE_DETALLE_ACTIVO, "fecha_de_caducidad": fecha_relativa(accesos_no_api, -DENTRO_DE_TOLERANCIA_MIN)}
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value=pase)
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    mocker.patch.object(accesos_no_api, "get_booth_locations", return_value=[LOCATION])
    mocker.patch.object(accesos_no_api, "validate_access_pass_location", return_value=False)
    registrar = mocker.patch.object(accesos_no_api, "_do_access", return_value=dict(ENTRADA_REGISTRADA))

    respuesta = accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})

    registrar.assert_called_once_with(pase, LOCATION, AREA, {})
    assert respuesta == ENTRADA_REGISTRADA


@pytest.mark.unit
def test_con_fecha_fija_no_se_puede_entrar_antes_de_la_tolerancia(accesos_no_api, mocker):
    """
    TB-180: un pase de fecha fija cuya cita es dentro de 1 hora, sin
    tolerancia configurada (15 min por defecto), debe detenerse con el aviso
    de que aún no es hora de entrada y no registrar la entrada.
    """
    pase = {
        **PASE_DETALLE_ACTIVO,
        "tipo_visita_pase": "fecha_fija",
        "fecha_de_expedicion": fecha_relativa(accesos_no_api, CITA_FUERA_DE_TOLERANCIA_MIN),
        "fecha_de_caducidad": fecha_relativa(accesos_no_api, VIGENTE_POR_MIN),
    }
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value=pase)
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    mocker.patch.object(accesos_no_api, "get_booth_locations", return_value=[LOCATION])
    mocker.patch.object(accesos_no_api, "get_config_accesos", return_value=dict(CONFIG_SIN_TOLERANCIA))
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="no es hora de entrada"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()


@pytest.mark.unit
def test_ubicacion_que_no_esta_en_el_pase_no_da_acceso(accesos_no_api, mocker):
    """
    TB-182: en una caseta de una ubicación que no está en el pase, do_access
    debe detenerse con el aviso de que la ubicación no está en el pase y no
    registrar la entrada. Si la registra, el pase sirve en lugares a los que
    no se le dio acceso.
    """
    pase = {
        **PASE_DETALLE_ACTIVO,
        "ubicacion": [OTRA_UBICACION],
        "fecha_de_caducidad": fecha_relativa(accesos_no_api, VIGENTE_POR_MIN),
    }
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value=pase)
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    mocker.patch.object(accesos_no_api, "get_booth_locations", return_value=[LOCATION])
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="no se encuentra en el pase"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()


# --- do access registro ---
@pytest.mark.unit
def test_visitante_que_ya_esta_dentro_no_vuelve_a_entrar(accesos_no_api, mocker):
    """
    TB-183: con un pase válido cuyo visitante ya está dentro de la ubicación,
    do_access debe detenerse con el aviso de que ya se encuentra dentro y no
    registrar otra entrada. Si la registra, la bitácora muestra a la misma
    persona dentro dos veces.
    """
    pase = {**PASE_DETALLE_ACTIVO, "fecha_de_caducidad": fecha_relativa(accesos_no_api, VIGENTE_POR_MIN)}
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value=pase)
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    mocker.patch.object(accesos_no_api, "get_booth_locations", return_value=[LOCATION])
    mocker.patch.object(accesos_no_api, "validate_access_pass_location", return_value=True)
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="ya se encuentra dentro de una ubicacion"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()


@pytest.mark.unit
def test_caseta_multiubicacion_registra_en_la_ubicacion_del_pase(accesos_no_api, mocker):
    """
    TB-184: en una caseta que atiende dos ubicaciones, un pase que solo es
    para la segunda debe dar acceso y registrar la entrada en la ubicación del
    pase, no en la de la caseta. Si se registra en la de la caseta, la persona
    aparece dentro de una planta a la que no tiene acceso.
    """
    pase = {
        **PASE_DETALLE_ACTIVO,
        "ubicacion": [OTRA_UBICACION],
        "fecha_de_caducidad": fecha_relativa(accesos_no_api, VIGENTE_POR_MIN),
    }
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value=pase)
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    mocker.patch.object(accesos_no_api, "get_booth_locations", return_value=[LOCATION, OTRA_UBICACION])
    mocker.patch.object(accesos_no_api, "validate_access_pass_location", return_value=False)
    registrar = mocker.patch.object(accesos_no_api, "_do_access", return_value=dict(ENTRADA_REGISTRADA))

    respuesta = accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})

    registrar.assert_called_once_with(pase, OTRA_UBICACION, AREA, {})
    assert respuesta == ENTRADA_REGISTRADA
