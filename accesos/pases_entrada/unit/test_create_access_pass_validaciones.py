# coding: utf-8

"""
Validaciones al crear un pase (create_access_pass, + Nuevo Pase y auto
registro) sin tocar preprod: se simula todo lo que la función consulta fuera
y se revisa que el pase no se guarde cuando no debe.
Notion: TB-202 a TB-206.
"""

import copy

import pytest

from .helpers import crear_pase_simulado, pase_nuevo
from ..data.pases_entrada_data import (
    CAMPOS_REQUERIDOS,
    TELEFONO_SIN_LADA,
    TELEFONO_CON_LETRAS,
    TELEFONO_CON_LADA,
    PASE_AUTO_REGISTRO,
    VISITA_A_UNIT,
    DIAS_VENCIDO,
    ACOMPANANTES_PASE,
)


@pytest.mark.unit
def test_pase_sin_ubicacion_perfil_ni_visita_a_responde_que_falta(accesos_no_api, mocker):
    """
    TB-202: un pase sin ubicaciones, perfil ni a quién visita debe detenerse
    con el error "Faltan campos requeridos" que nombra los tres, y no
    guardarse. Si se guarda, queda un pase que ninguna caseta puede validar.
    """
    guardar = crear_pase_simulado(accesos_no_api, mocker)
    pase = pase_nuevo(accesos_no_api, **{campo: [] for campo in CAMPOS_REQUERIDOS})

    with pytest.raises(Exception, match="Faltan campos requeridos") as error:
        accesos_no_api.create_access_pass(pase)
    for campo in CAMPOS_REQUERIDOS:
        assert campo in str(error.value), f"El error no nombra '{campo}': {error.value}"
    guardar.assert_not_called()


@pytest.mark.unit
def test_pase_de_web_con_telefono_mal_escrito_responde_un_error_claro(accesos_no_api, mocker):
    """
    TB-203: desde web el teléfono va con lada (+52 y 10 dígitos). Un teléfono
    sin lada o con letras debe detenerse con el error de teléfono y no
    guardar el pase. Si se guarda, el visitante no recibe el link por SMS.
    """
    guardar = crear_pase_simulado(accesos_no_api, mocker)

    for telefono in (TELEFONO_SIN_LADA, TELEFONO_CON_LETRAS):
        with pytest.raises(Exception, match="El telefono debe contener exactamente 10 digitos"):
            accesos_no_api.create_access_pass(pase_nuevo(accesos_no_api, telefono=telefono))
    guardar.assert_not_called()


@pytest.mark.unit
def test_en_auto_registro_el_telefono_va_sin_lada(accesos_no_api, mocker):
    """
    TB-204: en auto registro el visitante escribe su teléfono de 10 dígitos
    sin lada; con lada (+52…) debe detenerse con el error de teléfono y no
    guardar el pase. Con 10 dígitos sí pasa la validación.
    """
    guardar = crear_pase_simulado(accesos_no_api, mocker)
    auto_registro = {**copy.deepcopy(PASE_AUTO_REGISTRO), "visita_a": VISITA_A_UNIT}

    with pytest.raises(Exception, match="El telefono debe contener exactamente 10 digitos"):
        accesos_no_api.create_access_pass({**auto_registro, "telefono": TELEFONO_CON_LADA})
    guardar.assert_not_called()

    accesos_no_api.create_access_pass(auto_registro)
    guardar.assert_called_once()


@pytest.mark.unit
def test_no_se_puede_crear_un_pase_con_fecha_de_visita_en_el_pasado(accesos_no_api, mocker):
    """
    TB-205: un pase con la fecha de visita de ayer debe detenerse con el
    error "No se puede crear un pase con fecha de visita en el pasado." y no
    guardarse. Si se guarda, nace un pase que ya no sirve.
    """
    guardar = crear_pase_simulado(accesos_no_api, mocker)

    with pytest.raises(Exception, match="No se puede crear un pase con fecha de visita en el pasado"):
        accesos_no_api.create_access_pass(pase_nuevo(accesos_no_api, dias_desde=DIAS_VENCIDO))
    guardar.assert_not_called()


@pytest.mark.unit
def test_no_se_puede_crear_un_pase_con_mas_acompanantes_de_los_permitidos(accesos_no_api, mocker):
    """
    TB-206: un pase que permite 1 acompañante pero trae 2 en la lista debe
    detenerse con el error de que la lista excede los acompañantes
    permitidos, y no guardarse. Si se guarda, entra más gente de la que el
    anfitrión autorizó.
    """
    guardar = crear_pase_simulado(accesos_no_api, mocker)
    pase = pase_nuevo(accesos_no_api, acompanantes=1, acompanantes_grupo=copy.deepcopy(ACOMPANANTES_PASE))

    with pytest.raises(Exception, match="excede el permitido para este pase"):
        accesos_no_api.create_access_pass(pase)
    guardar.assert_not_called()
