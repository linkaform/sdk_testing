# coding: utf-8

"""
Editar una incidencia (update_incidence) y el tiempo transcurrido al cierre
(_tiempo_cierre_answers) sin tocar la cuenta: se simulan la incidencia como
estaba, el guardia de la sesión y el guardado.
Notion: TB-279 a TB-283 (pendientes de dar de alta).
"""

import pytest

from ..data.incidencias_data import (
    GUARDIA_SESION,
    EDITADO_OK,
    GUARDADO_ERROR,
    FOLIO_INCIDENCIA,
    INCIDENCIA_ANTES,
    SEGUIMIENTO_EXISTENTE,
    SEGUIMIENTO_NUEVO,
    TIEMPO_CIERRE_GUARDADO,
)

pytestmark = pytest.mark.back("sanic")


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
    TB-279: al editar, el front manda todos los seguimientos. El que ya
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
    TB-280: después de guardar la edición se registra el cambio en el
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
    TB-281: si LinkaForm rechaza la edición, el historial no debe decir que
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
    TB-282: si una incidencia cerrada se reabre, "Tiempo transcurrido al
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
    TB-283: editar una incidencia que sigue cerrada vuelve a mandar el tiempo
    que ya tenía, sin recalcularlo (el PATCH reemplaza las respuestas
    completas: si no se manda, se pierde).
    """
    acc = accesos_no_api
    creada = mocker.patch.object(acc, "_incidencia_creada_en")
    antes = {**INCIDENCIA_ANTES, "estatus": "cerrado", "tiempo_transcurrido_cierre": TIEMPO_CIERRE_GUARDADO}

    res = acc._tiempo_cierre_answers(antes, None)

    assert res == {acc.incidence_fields["tiempo_transcurrido_cierre"]: TIEMPO_CIERRE_GUARDADO}
    assert not creada.called, "Recalculó el tiempo de una incidencia que ya estaba cerrada"
