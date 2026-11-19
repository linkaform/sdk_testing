# coding: utf-8

"""
Lista de incidencias (get_list_incidences en Sanic: Abiertas y Cerradas) con
la consulta simulada.
Notion: TB-350.
"""

from bson import ObjectId
import pytest

from ..data.incidencias_data import (
    FOLIO_INCIDENCIA,
    INCIDENCIA_SIN_PRIORIDAD,
)

pytestmark = pytest.mark.back("sanic")


def test_lista_de_incidencias_no_truena_con_una_sin_prioridad(accesos_no_api, mocker):
    """
    TB-350: una incidencia guardada sin prioridad sale en la lista. Hoy
    format_incidencia hace .title() sobre la lista vacía que pone de default.
    El AttributeError se vuelve falla aquí porque lkf_back lo marcaría como
    SKIPPED ("falta en sanic").
    """
    acc = accesos_no_api
    cr = mocker.MagicMock()
    cr.aggregate.return_value = [{"_id": ObjectId(), **INCIDENCIA_SIN_PRIORIDAD}]
    mocker.patch.object(acc, "cr", cr)

    try:
        incidencias = acc.get_list_incidences([], "")
    except AttributeError as error:
        pytest.fail(f"La lista truena con una incidencia sin prioridad: {error}")

    assert [i["folio"] for i in incidencias] == [FOLIO_INCIDENCIA]
