# coding: utf-8

"""Incidencias: crear (create_incidence), editar (update_incidence) y tiempo
transcurrido al cierre (_tiempo_cierre_answers), sin tocar la cuenta.
Notion: TB-279 a TB-288.

Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS:
./lkf test corre este archivo cuando cambia alguna funcion de C10_TRIGGERS.
La seccion la sirve Sanic en prod: los tests llevan back("sanic") y en addons
salen SKIPPED.
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
    EDITADO_OK,
    FOLIO_INCIDENCIA,
    INCIDENCIA_ANTES,
    SEGUIMIENTO_EXISTENTE,
    SEGUIMIENTO_NUEVO,
    TIEMPO_CIERRE_GUARDADO,
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["_crear_falla_de_incidencia", "_reporta_sesion", "_tiempo_cierre_answers", "_url_registro_lkf", "create_incidence", "update_incidence"]


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


def editar_simulado(acc, mocker, antes=INCIDENCIA_ANTES, editado=EDITADO_OK):
    mocker.patch.object(acc, "_incidencia_formateada", return_value=dict(antes))
    mocker.patch.object(acc, "_reporta_sesion", return_value=GUARDIA_SESION)
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value={})
    mocker.patch.object(acc, "get_record_by_folio", return_value={"_id": INCIDENCIA_ANTES["_id"]})
    mocker.patch.object(acc, "agregar_tipo_al_catalogo")
    return {
        "guardar": mocker.patch.object(acc.net, "patch_forms_answers", return_value=dict(editado)),
        "historial": mocker.patch.object(acc, "registrar_cambios_incidencia"),
    }


@pytest.mark.unit
@pytest.mark.target("update_incidence", "_reporta_sesion")
def test_seguimiento_nuevo_lo_registra_el_guardia_de_la_sesion_y_el_existente_conserva_el_suyo(accesos_no_api, mocker):
    """
    TB-284: al editar, el front manda todos los seguimientos. El que ya
    existía conserva a quien lo registró y el nuevo (sin la llave) toma al
    guardia de la sesión. Si no, cada edición cambia el autor de todo el historial.
    """
    acc = accesos_no_api
    mocks = editar_simulado(acc, mocker)

    acc.update_incidence({"seguimientos_incidencia": [dict(SEGUIMIENTO_EXISTENTE), dict(SEGUIMIENTO_NUEVO)]},
                         FOLIO_INCIDENCIA)

    f = acc.incidence_fields
    existente, nuevo = mocks["guardar"].call_args.args[0]["answers"][f["seguimientos_incidencia"]]
    assert existente[f["registrado_por_seguimiento"]] == SEGUIMIENTO_EXISTENTE["registrado_por"]
    assert nuevo[f["registrado_por_seguimiento"]] == GUARDIA_SESION


@pytest.mark.unit
@pytest.mark.target("update_incidence")
def test_editar_registra_el_historial_con_la_version_de_antes(accesos_no_api, mocker):
    """
    TB-285: después de guardar la edición se registra el cambio en el
    historial con la incidencia como estaba antes, sobre su folio. Es lo que
    muestra "Historial" en el detalle de la incidencia.
    """
    acc = accesos_no_api
    mocks = editar_simulado(acc, mocker)

    acc.update_incidence({"comentario_incidencia": "Comentario editado QA"}, FOLIO_INCIDENCIA)

    mocks["historial"].assert_called_once_with(INCIDENCIA_ANTES, folio=FOLIO_INCIDENCIA)


@pytest.mark.unit
@pytest.mark.target("update_incidence")
def test_si_la_edicion_no_se_guarda_no_registra_historial(accesos_no_api, mocker):
    """
    TB-286: si LinkaForm rechaza la edición, el historial no debe decir que
    la incidencia cambió.
    """
    acc = accesos_no_api
    mocks = editar_simulado(acc, mocker, editado=GUARDADO_ERROR)

    acc.update_incidence({"comentario_incidencia": "Comentario editado QA"}, FOLIO_INCIDENCIA)

    assert not mocks["historial"].called, "Registró en el historial una edición que no se guardó"


@pytest.mark.unit
@pytest.mark.target("_tiempo_cierre_answers")
def test_reabrir_una_incidencia_cerrada_limpia_el_tiempo_al_cierre(accesos_no_api):
    """
    TB-287: si una incidencia cerrada se reabre, "Tiempo transcurrido al
    cierre" se limpia; se vuelve a calcular cuando se cierre otra vez.
    """
    acc = accesos_no_api
    antes = {**INCIDENCIA_ANTES, "estatus": "cerrado", "tiempo_transcurrido_cierre": TIEMPO_CIERRE_GUARDADO}

    res = acc._tiempo_cierre_answers(antes, "abierto")

    assert res == {acc.incidence_fields["tiempo_transcurrido_cierre"]: ""}


@pytest.mark.unit
@pytest.mark.target("_tiempo_cierre_answers")
def test_editar_una_incidencia_cerrada_conserva_su_tiempo_al_cierre(accesos_no_api, mocker):
    """
    TB-288: editar una incidencia que sigue cerrada vuelve a mandar el tiempo
    que ya tenía, sin recalcularlo (el PATCH reemplaza las respuestas
    completas: si no se manda, se pierde).
    """
    acc = accesos_no_api
    creada = mocker.patch.object(acc, "_incidencia_creada_en")
    antes = {**INCIDENCIA_ANTES, "estatus": "cerrado", "tiempo_transcurrido_cierre": TIEMPO_CIERRE_GUARDADO}

    res = acc._tiempo_cierre_answers(antes, None)

    assert res == {acc.incidence_fields["tiempo_transcurrido_cierre"]: TIEMPO_CIERRE_GUARDADO}
    assert not creada.called, "Recalculó el tiempo de una incidencia que ya estaba cerrada"
