# coding: utf-8

"""
Con qué estatus nace un pase y si se autoriza solo (create_access_pass, +
Nuevo Pase, Nueva Visita y auto registro) sin tocar preprod: se simula todo
lo que la función consulta fuera y se revisa el estatus y la autorización que
se mandan a guardar.
Notion: TB-207 a TB-211.
"""

import pytest

from .helpers import crear_pase_simulado, pase_nuevo
from ..data.pases_entrada_data import ESTATUS_PROCESO


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
