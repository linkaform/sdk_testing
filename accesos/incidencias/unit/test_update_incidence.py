# coding: utf-8

"""
Editar una incidencia (update_incidence en Sanic: modal de edición y detalle)
sin tocar la cuenta: se simulan la incidencia de antes y el guardado, y se
revisa qué se manda a guardar.
Notion: TB-346 y TB-348.
"""

import pytest

from .helpers import editar_simulado
from ..data.incidencias_data import (
    FOLIO_INCIDENCIA,
    INCIDENCIA_CON_FALLA,
    EDICION_CATALOGO,
    EDICION_SIN_LIGA,
)

pytestmark = pytest.mark.back("sanic")


@pytest.mark.bug(1601)
def test_editar_no_guarda_categoria_tipo_ni_subcategoria_fuera_del_catalogo(accesos_no_api, mocker):
    """
    TB-346: al editar, la categoría, el tipo y la subcategoría van en el
    catálogo de incidencias. update_incidence de Sanic además los escribe como
    respuestas sueltas (addons y update_incidence_seguimiento los saltan), y la
    subcategoría suelta se guarda aunque venga vacía.
    Ticket 2611-1601.
    """
    acc = accesos_no_api
    guardar = editar_simulado(acc, mocker, antes=INCIDENCIA_CON_FALLA)["guardar"]

    acc.update_incidence(dict(EDICION_CATALOGO), FOLIO_INCIDENCIA)

    f = acc.incidence_fields
    answers = guardar.call_args.args[0]["answers"]
    sueltos = [campo for campo in ("categoria", "incidencia", "sub_categoria") if f[campo] in answers]
    assert not sueltos, f"Se guardaron fuera del catálogo: {sueltos}"


@pytest.mark.bug(1602)
def test_editar_conserva_la_liga_a_la_falla_generada(accesos_no_api, mocker):
    """
    TB-348: editar una incidencia que se reportó como falla no manda la liga
    (el front no la tiene en el formulario); el back debe conservarla de la
    versión de antes para que la incidencia siga ligada a su falla.
    Ticket 2611-1602.
    """
    acc = accesos_no_api
    guardar = editar_simulado(acc, mocker, antes=INCIDENCIA_CON_FALLA)["guardar"]

    acc.update_incidence(dict(EDICION_SIN_LIGA), FOLIO_INCIDENCIA)

    answers = guardar.call_args.args[0]["answers"]
    assert acc.incidence_fields["falla_generada_url"] in answers, "Editar borra la liga a la falla"
