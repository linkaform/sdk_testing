# coding: utf-8

"""
Armar las incidencias que se registran desde el check de un rondín
(format_grupo_incidencias en Sanic) sin tocar la cuenta.
Notion: TB-349.
"""

import pytest

from ..data.incidencias_data import (
    GUARDIA_SESION,
    INCIDENCIA_DE_RONDIN,
    FOLIO_CHECK_RONDIN,
)

pytestmark = pytest.mark.back("sanic")


def test_incidencia_de_rondin_se_arma_con_su_estatus(accesos_no_api, mocker):
    """
    TB-349: la incidencia capturada en el check de un rondín se arma para la
    bitácora de incidencias y nace con estatus. Hoy truena con KeyError
    'comentario_incidente_bitacora': lo busca en los campos de incidencias y
    solo existe en los del rondín.
    """
    acc = accesos_no_api
    mocker.patch.object(acc, "get_employee_name", return_value=GUARDIA_SESION)

    incidencias = acc.format_grupo_incidencias(
        [{acc.f["incidente_open"]: INCIDENCIA_DE_RONDIN}], {}, FOLIO_CHECK_RONDIN
    )

    f = acc.incidence_fields
    assert incidencias[0][f["tipo_incidencia"]] == INCIDENCIA_DE_RONDIN
    assert f["estatus"] in incidencias[0], "La incidencia del rondín nace sin estatus"
