# coding: utf-8

"""
+ Nuevo Pase (create_access_pass desde web): el estatus con el que nace el
pase según los toggles del formulario, y la configuración de la ubicación que
el formulario pide al elegir la ubicación (get_config_modulo_seguridad).
Notion: TB-117 a TB-119 y TB-122.
"""

import pytest

from .fixtures import *
from ..data.pases_entrada_data import (
    LOCATION,
    TAB_ACTIVOS,
    ESTATUS_ACTIVO,
    ESTATUS_PROCESO,
    LIMITE_LISTA,
    LLAVES_CONFIG_UBICACION,
    LLAVES_LISTA_CONFIG,
    REQUERIMIENTOS_VALIDOS,
    VALORES_SI_NO,
)
from .helpers import crear_pase


@pytest.mark.integration
def test_pase_con_auto_activacion_nace_activo(acceso_obj, mock_pase_auto_activacion):
    """
    TB-117: con "Activar pase por defecto" prendido el pase debe nacer
    'activo' aunque la ubicación pida foto e identificación y no las traiga,
    y aparecer en Activos. Si nace en proceso, el guardia tiene que esperar a
    que el visitante complete un pase que el anfitrión ya quería activo.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_auto_activacion)

    estatus = acceso_obj.get_detail_access_pass(pase_id).get("estatus")
    assert estatus == ESTATUS_ACTIVO, f"El pase con auto activación nació '{estatus}'"

    activos = acceso_obj.get_my_pases(
        tab_status=TAB_ACTIVOS, search_name=mock_pase_auto_activacion["nombre"], limit=LIMITE_LISTA
    )
    assert pase_id in {p["_id"] for p in activos["records"]}, "El pase con auto activación no aparece en Activos"


@pytest.mark.integration
def test_pase_sin_foto_ni_identificacion_requeridas_nace_activo(acceso_obj, mock_pase_sin_requisitos):
    """
    TB-118: sin auto activación y con foto e identificación apagadas por el
    admin, el visitante no tiene nada que completar: el pase debe nacer
    'activo'. Si nace en proceso, se queda ahí para siempre porque el link
    no le pide nada al visitante.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_sin_requisitos)

    estatus = acceso_obj.get_detail_access_pass(pase_id).get("estatus")
    assert estatus == ESTATUS_ACTIVO, f"El pase sin requisitos nació '{estatus}'"


@pytest.mark.integration
def test_pase_que_pide_foto_e_identificacion_no_nace_activo(acceso_obj, mock_pase_pide_foto_e_identificacion):
    """
    TB-119: sin auto activación, con foto e identificación prendidas y sin
    traerlas, el pase debe nacer en 'proceso' hasta que el visitante las
    suba por el link. Si nace activo, el visitante entra sin foto ni
    identificación aunque la ubicación las pide.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_pide_foto_e_identificacion)

    estatus = acceso_obj.get_detail_access_pass(pase_id).get("estatus")
    assert estatus == ESTATUS_PROCESO, f"El pase sin foto ni identificación nació '{estatus}'"


@pytest.mark.integration
def test_config_de_la_ubicacion_trae_lo_que_usa_nuevo_pase(acceso_obj):
    """
    TB-122: al elegir la ubicación, + Nuevo Pase pide su configuración y con
    ella decide qué toggles mostrar (foto, identificación, "Activar pase por
    defecto", acompañantes requeridos). Debe regresar todas las llaves, las
    listas como listas, los requerimientos en minúsculas como los busca el
    front, y los toggles en "sí"/"no".
    """
    config = acceso_obj.get_config_modulo_seguridad(ubicaciones=[LOCATION])

    assert set(config) == LLAVES_CONFIG_UBICACION, f"Llaves inesperadas: {sorted(config)}"
    for llave in LLAVES_LISTA_CONFIG:
        assert isinstance(config[llave], list), f"'{llave}' no es lista: {config[llave]!r}"

    assert set(config["requerimientos"]) <= REQUERIMIENTOS_VALIDOS, (
        f"Requerimientos que el front no reconoce: {config['requerimientos']}"
    )
    assert config["auto_activacion"] in VALORES_SI_NO, f"auto_activacion = {config['auto_activacion']!r}"
    assert config["acompanantes_requeridos"] in VALORES_SI_NO, (
        f"acompanantes_requeridos = {config['acompanantes_requeridos']!r}"
    )
    assert [u["name"] for u in config["ubicaciones_info"]] == [LOCATION], (
        f"ubicaciones_info no es de {LOCATION}: {config['ubicaciones_info']}"
    )
