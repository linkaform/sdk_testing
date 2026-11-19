# coding: utf-8

"""
Editar una incidencia (update_incidence en Sanic: modal de edición y detalle)
sin tocar la cuenta: se simulan la incidencia de antes y el guardado, y se
revisa qué se manda a guardar.
Notion: TB-346.
"""

import pytest

from .helpers import edicion_simulada
from ..data.incidencias_data import (
    FOLIO_INCIDENCIA,
    EDICION_CATALOGO,
)

pytestmark = pytest.mark.back("sanic")


def test_editar_no_guarda_categoria_tipo_ni_subcategoria_fuera_del_catalogo(accesos_no_api, mocker):
    """
    TB-346: al editar, la categoría, el tipo y la subcategoría van en el
    catálogo de incidencias. update_incidence de Sanic además los escribe como
    respuestas sueltas (addons y update_incidence_seguimiento los saltan), y la
    subcategoría suelta se guarda aunque venga vacía.
    """
    acc = accesos_no_api
    guardar = edicion_simulada(acc, mocker)

    acc.update_incidence(dict(EDICION_CATALOGO), FOLIO_INCIDENCIA)

    f = acc.incidence_fields
    answers = guardar.call_args.args[0]["answers"]
    sueltos = [campo for campo in ("categoria", "incidencia", "sub_categoria") if f[campo] in answers]
    assert not sueltos, f"Se guardaron fuera del catálogo: {sueltos}"
