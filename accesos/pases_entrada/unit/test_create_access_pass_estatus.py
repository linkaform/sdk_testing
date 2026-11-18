# coding: utf-8

"""
Con qué estatus nace un pase y si se autoriza solo (create_access_pass, +
Nuevo Pase, Nueva Visita y auto registro) sin tocar preprod: se simula todo
lo que la función consulta fuera y se revisa el estatus y la autorización que
se mandan a guardar.
Notion: TB-207 a TB-211.
"""

import copy

import pytest
from lkf_back import de

from .helpers import crear_pase_simulado, pase_nuevo
from ..data.pases_entrada_data import (
    ESTATUS_PROCESO,
    ESTATUS_ACTIVO,
    HABILITAR_SI,
    PASE_AUTO_REGISTRO,
    VISITA_A_UNIT,
    AUTORIZACION_PASE,
    AUTO_ACTIVACION_SI,
)


def pase_guardado(guardar):
    """Answers del pase que create_access_pass mandó a guardar."""
    guardar.assert_called_once()
    return guardar.call_args.args[0]["answers"]


@pytest.mark.unit
def test_pase_de_web_sin_toggles_nace_en_proceso(accesos_no_api, mocker):
    """
    TB-207: un pase de + Nuevo Pase (web) sin auto activación ni toggles de
    foto o identificación debe guardarse en 'proceso', para que el visitante
    lo complete con el link. Si nace activo, entra sin foto ni
    identificación.
    """
    acc = accesos_no_api
    guardar = crear_pase_simulado(acc, mocker)

    acc.create_access_pass(pase_nuevo(acc))

    estatus = pase_guardado(guardar)[acc.pase_entrada_fields["status_pase"]]
    assert estatus == ESTATUS_PROCESO, f"El pase de web nació {estatus!r}"


@pytest.mark.unit
def test_pase_de_web_con_toggles_se_evalua_al_crearse(accesos_no_api, mocker):
    """
    TB-208: si el admin manda los toggles de foto e identificación desde +
    Nuevo Pase, el pase de web ya no nace en 'proceso' fijo: debe guardarse
    con el estatus que calcula access_pass_set_status. Si se queda en
    'proceso', un pase que ya no pide nada no se puede usar.
    """
    acc = accesos_no_api
    guardar = crear_pase_simulado(acc, mocker)
    evaluar = mocker.patch.object(
        de(acc, "access_pass_set_status"), "access_pass_set_status", return_value=ESTATUS_ACTIVO
    )

    acc.create_access_pass(pase_nuevo(acc, habilitar_fotografia=HABILITAR_SI, habilitar_identificacion=HABILITAR_SI))

    evaluar.assert_called_once()
    estatus = pase_guardado(guardar)[acc.pase_entrada_fields["status_pase"]]
    assert estatus == ESTATUS_ACTIVO, f"El pase con toggles nació {estatus!r}"


@pytest.mark.unit
def test_pase_de_auto_registro_no_se_autoriza_solo(accesos_no_api, mocker):
    """
    TB-209: un pase de auto registro lo llena el visitante, no un empleado;
    create_access_pass no debe pedir la autorización ni guardar quién lo
    autorizó, para que caiga en Por autorizar. Si se autoriza solo, cualquiera
    que llene el formulario entra sin que nadie lo apruebe.
    """
    acc = accesos_no_api
    guardar = crear_pase_simulado(acc, mocker)
    autorizar = mocker.patch.object(
        de(acc, "autorizar_pase_acceso"), "autorizar_pase_acceso", return_value=dict(AUTORIZACION_PASE)
    )

    acc.create_access_pass({**copy.deepcopy(PASE_AUTO_REGISTRO), "visita_a": VISITA_A_UNIT})

    autorizar.assert_not_called()
    answers = pase_guardado(guardar)
    assert acc.pase_entrada_fields["catalago_autorizado_por"] not in answers, "El pase de auto registro se autorizó solo"


@pytest.mark.unit
def test_pase_de_nueva_visita_se_autoriza_con_quien_lo_crea(accesos_no_api, mocker):
    """
    TB-210: un pase de Nueva Visita lo crea el empleado que invita;
    create_access_pass debe guardarlo autorizado con lo que regresa
    autorizar_pase_acceso y con el estatus que calcula access_pass_set_status.
    Si no se autoriza, el pase se queda en Por autorizar aunque el anfitrión
    ya lo avaló.
    """
    acc = accesos_no_api
    guardar = crear_pase_simulado(acc, mocker)
    autorizar = mocker.patch.object(
        de(acc, "autorizar_pase_acceso"), "autorizar_pase_acceso", return_value=dict(AUTORIZACION_PASE)
    )
    mocker.patch.object(de(acc, "access_pass_set_status"), "access_pass_set_status", return_value=ESTATUS_ACTIVO)

    acc.create_access_pass(pase_nuevo(acc, created_from="nueva_visita"))

    autorizar.assert_called_once()
    answers = pase_guardado(guardar)
    assert answers[acc.pase_entrada_fields["catalago_autorizado_por"]] == AUTORIZACION_PASE
    assert answers[acc.pase_entrada_fields["status_pase"]] == ESTATUS_ACTIVO


@pytest.mark.unit
def test_pase_con_auto_activacion_se_guarda_activo(accesos_no_api, mocker):
    """
    TB-211: con "Activar pase por defecto" (auto_activacion 'sí'), un pase de
    web sin foto ni identificación debe guardarse 'activo', aunque
    access_pass_set_status diga que le faltan datos. Si se queda en
    'proceso', la auto activación no sirve.
    """
    acc = accesos_no_api
    guardar = crear_pase_simulado(acc, mocker)
    mocker.patch.object(de(acc, "access_pass_set_status"), "access_pass_set_status", return_value=ESTATUS_PROCESO)

    acc.create_access_pass(pase_nuevo(acc, auto_activacion=AUTO_ACTIVACION_SI, foto=[], identificacion=[]))

    estatus = pase_guardado(guardar)[acc.pase_entrada_fields["status_pase"]]
    assert estatus == ESTATUS_ACTIVO, f"El pase con auto activación nació {estatus!r}"
