# coding: utf-8

"""
Crear una incidencia (create_incidence) sin tocar la cuenta: se simulan la
metadata de la forma, el guardia de la sesión y el guardado, y se revisa lo
que create_incidence manda a guardar.
Notion: TB-279 a TB-283.
"""

import pytest

from ..data.incidencias_data import (
    LOCATION,
    AREA,
    INCIDENCIA_NUEVA,
    GUARDIA_SESION,
    GUARDADO_OK,
    GUARDADO_ERROR,
    REPORTAR_FALLA,
    AFECTACION_SIN_MONTO,
    AFECTACION_CON_MONTO,
)

pytestmark = pytest.mark.back("sanic")


def crear_simulado(acc, mocker, guardado=GUARDADO_OK):
    """Simula todo lo que sale a la red; regresa los mocks que revisan los tests."""
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value={})
    mocker.patch.object(acc, "_reporta_sesion", return_value=GUARDIA_SESION)
    return {
        "guardar": mocker.patch.object(acc.lkf_api, "post_forms_answers", return_value=dict(guardado)),
        "falla": mocker.patch.object(acc, "_crear_falla_de_incidencia", return_value={"ok": True}),
        "catalogo": mocker.patch.object(acc, "agregar_tipo_al_catalogo"),
        "historial": mocker.patch.object(acc, "registrar_cambios_incidencia"),
    }


@pytest.mark.unit
@pytest.mark.target("create_incidence", "_reporta_sesion")
def test_incidencia_nueva_nace_abierta_con_catalogo_ubicacion_prioridad_y_quien_reporta(accesos_no_api, mocker):
    """
    TB-279: con el payload de Nueva incidencia, create_incidence debe guardar
    la incidencia 'abierto', la categoría y el tipo en su catálogo, la
    ubicación y la caseta, la prioridad en minúsculas (la opción de la forma)
    y como "Reporta" al guardia de la sesión cuando el front lo manda vacío.
    Si falta algo, la incidencia no sale en su filtro o no se sabe quién la levantó.
    """
    acc = accesos_no_api
    mocks = crear_simulado(acc, mocker)

    acc.create_incidence(dict(INCIDENCIA_NUEVA))

    f = acc.incidence_fields
    answers = mocks["guardar"].call_args.args[0]["answers"]
    assert answers[f["estatus"]] == "abierto"
    assert answers[f["incidencia_catalog"]][f["categoria"]] == INCIDENCIA_NUEVA["categoria"]
    assert answers[f["incidencia_catalog"]][f["incidencia"]] == INCIDENCIA_NUEVA["incidencia"]
    ubicacion = answers[f["ubicacion_incidencia_catalog"]]
    assert ubicacion[f["ubicacion_incidencia"]] == LOCATION
    assert ubicacion[f["area_incidencia"]] == AREA
    assert answers[f["prioridad_incidencia"]] == "alta"
    assert answers[f["reporta_incidencia_catalog"]][f["reporta_incidencia"]] == GUARDIA_SESION


@pytest.mark.unit
@pytest.mark.target("create_incidence")
def test_subcategoria_vacia_y_llaves_que_la_forma_no_conoce_no_rompen_la_incidencia(accesos_no_api, mocker):
    """
    TB-280: el catálogo ya no tiene subcategoría y el front puede mandar
    llaves de más. Una subcategoría vacía no se debe escribir y una llave que
    la forma no conoce se ignora: antes tronaban con KeyError y la incidencia
    completa no se creaba.
    """
    acc = accesos_no_api
    mocks = crear_simulado(acc, mocker)

    acc.create_incidence({**INCIDENCIA_NUEVA, "llave_que_no_existe": "x"})

    f = acc.incidence_fields
    answers = mocks["guardar"].call_args.args[0]["answers"]
    assert f["sub_categoria"] not in answers[f["incidencia_catalog"]], "Se guardó una subcategoría vacía"
    assert "x" not in answers.values(), "Se guardó la llave que la forma no conoce"


@pytest.mark.unit
@pytest.mark.target("create_incidence")
def test_afectacion_sin_monto_no_manda_el_monto(accesos_no_api, mocker):
    """
    TB-281: el monto estimado de la afectación patrimonial es decimal y
    opcional. Si viene vacío no se manda (un '' en un campo decimal hace que
    LinkaForm rechace el registro); si viene con valor, se guarda.
    """
    acc = accesos_no_api
    mocks = crear_simulado(acc, mocker)

    acc.create_incidence({**INCIDENCIA_NUEVA,
                          "afectacion_patrimonial_incidencia": [dict(AFECTACION_SIN_MONTO), dict(AFECTACION_CON_MONTO)]})

    f = acc.incidence_fields
    sin_monto, con_monto = mocks["guardar"].call_args.args[0]["answers"][f["afectacion_patrimonial_incidencia"]]
    assert f["monto_estimado"] not in sin_monto, f"Se mandó el monto vacío: {sin_monto}"
    assert con_monto[f["monto_estimado"]] == AFECTACION_CON_MONTO["monto_estimado"]


@pytest.mark.unit
@pytest.mark.target("create_incidence", "_url_registro_lkf")
def test_reportar_como_falla_liga_la_incidencia_con_su_falla(accesos_no_api, mocker):
    """
    TB-282: con "Reportar como falla", la incidencia y la falla deben nacer
    ligadas: la incidencia guarda la liga a la falla (con un id que ya trae)
    y la falla se crea con el id de la incidencia. Si se crean por separado,
    nadie llega de una a la otra.
    """
    acc = accesos_no_api
    mocks = crear_simulado(acc, mocker)

    res = acc.create_incidence({**INCIDENCIA_NUEVA, "reportar_falla": dict(REPORTAR_FALLA)})

    f = acc.incidence_fields
    guardado = mocks["guardar"].call_args.args[0]
    incidencia_id = guardado["id"]
    _, reportar, falla_id, liga_incidencia = mocks["falla"].call_args.args
    assert reportar == REPORTAR_FALLA
    assert liga_incidencia == incidencia_id, "La falla no quedó ligada a la incidencia"
    assert guardado["answers"][f["falla_generada_url"]].endswith(f"/records/detail/{falla_id}")
    assert res["falla"] == {"ok": True}


@pytest.mark.unit
@pytest.mark.target("create_incidence")
def test_si_la_incidencia_no_se_guarda_no_crea_falla_ni_historial(accesos_no_api, mocker):
    """
    TB-283: si LinkaForm rechaza la incidencia, no se debe crear la falla
    ligada ni el registro de historial ni el tipo en el catálogo: quedarían
    huérfanos apuntando a una incidencia que no existe.
    """
    acc = accesos_no_api
    mocks = crear_simulado(acc, mocker, guardado=GUARDADO_ERROR)

    acc.create_incidence({**INCIDENCIA_NUEVA, "reportar_falla": dict(REPORTAR_FALLA)})

    assert not mocks["falla"].called, "Creó la falla de una incidencia que no se guardó"
    assert not mocks["historial"].called
    assert not mocks["catalogo"].called
