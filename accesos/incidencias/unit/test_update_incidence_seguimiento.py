# coding: utf-8

"""
Agregar un seguimiento a una incidencia (update_incidence_seguimiento en
Sanic) sin tocar la cuenta: se simulan la incidencia de antes y el guardado,
y se revisa qué se manda a guardar.
Notion: TB-347.
"""

import pytest

from .helpers import edicion_simulada
from ..data.incidencias_data import (
    FOLIO_INCIDENCIA,
    SEGUIMIENTO_NUEVO,
)

pytestmark = pytest.mark.back("sanic")


def test_agregar_seguimiento_conserva_la_liga_a_la_falla_y_los_datos_del_robo(accesos_no_api, mocker):
    """
    TB-347: el seguimiento rearma toda la incidencia para guardarla; si deja
    fuera la liga a la falla y los datos del robo (placas, marca), se borran de
    la incidencia al agregar un seguimiento.
    """
    acc = accesos_no_api
    guardar = edicion_simulada(acc, mocker)

    acc.update_incidence_seguimiento(FOLIO_INCIDENCIA, dict(SEGUIMIENTO_NUEVO), "Abierto")

    f = acc.incidence_fields
    answers = guardar.call_args.args[0]["answers"]
    faltan = [campo for campo in ("falla_generada_url", "placas", "marca") if f[campo] not in answers]
    assert not faltan, f"El seguimiento borra: {faltan}"
