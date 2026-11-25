# coding: utf-8

"""
Cerrar una incidencia (botón Cerrar incidencia del detalle; update_incidence
y _tiempo_cierre_answers en Sanic) sin tocar la cuenta: se simula cuándo se
creó la incidencia y el guardado, y se revisa qué se manda a guardar.
Notion: TB-391 y TB-392.
"""

from datetime import datetime, timedelta, timezone

import pytest

from ..data.incidencias_data import (
    INCIDENCIA_ANTES,
    CREADA_HACE,
    TIEMPO_CIERRE_CALCULADO,
)

pytestmark = pytest.mark.back("sanic")


def creada_hace(acc, mocker):
    """Simula que la incidencia se creó hace CREADA_HACE."""
    creada = datetime.now(timezone.utc) - timedelta(**CREADA_HACE)
    return mocker.patch.object(acc, "_incidencia_creada_en", return_value=creada)


@pytest.mark.unit
@pytest.mark.target("_tiempo_cierre_answers")
def test_cerrar_una_incidencia_abierta_calcula_el_tiempo_al_cierre(accesos_no_api, mocker):
    """
    TB-391: al pasar una incidencia abierta a cerrado se guarda en "Tiempo
    transcurrido al cierre" cuánto tardó desde que se creó, en texto legible.
    Es lo que el detalle muestra de una incidencia cerrada.
    """
    acc = accesos_no_api
    creada_hace(acc, mocker)

    res = acc._tiempo_cierre_answers(dict(INCIDENCIA_ANTES), "cerrado")

    assert res == {acc.incidence_fields["tiempo_transcurrido_cierre"]: TIEMPO_CIERRE_CALCULADO}
