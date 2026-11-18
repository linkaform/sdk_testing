# coding: utf-8

"""
Con qué estatus nace un pase y si se autoriza solo (create_access_pass, +
Nuevo Pase, Nueva Visita y auto registro) sin tocar preprod: se simula todo
lo que la función consulta fuera y se revisa el estatus y la autorización que
se mandan a guardar.
Notion: TB-207 a TB-211.
"""

import pytest
from lkf_back import de

from .helpers import crear_pase_simulado, pase_nuevo
from ..data.pases_entrada_data import (
    ESTATUS_PROCESO,
    ESTATUS_ACTIVO,
    HABILITAR_SI,
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
