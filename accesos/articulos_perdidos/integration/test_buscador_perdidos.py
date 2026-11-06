# coding: utf-8

"""
Buscador de la lista de artículos perdidos (get_search_fields_perdidos,
get_search_counts_perdidos y get_list_article_lost con facets, como el front).
Notion: TB-151.
"""

import pytest

from .fixtures import *
from ..data.perdidos_data import (
    LOCATION,
    ESTATUS_TODOS,
    FACET_NOMBRE,
    LIMITE_LISTA,
)


@pytest.mark.integration
def test_buscador_de_perdidos_encuentra_el_articulo(acceso_obj, articulo_pendiente):
    """
    TB-151: el buscador ofrece el campo Nombre y, al escribir el nombre de un
    artículo, lo cuenta y lo trae. Si no, el guardia no encuentra el artículo
    cuando alguien viene a reclamarlo.
    """
    nombre = articulo_pendiente["articulo_perdido"]

    campos = {c["key"]: c for c in acceso_obj.get_search_fields_perdidos()}
    assert FACET_NOMBRE in campos, f"El buscador no ofrece el campo '{FACET_NOMBRE}': {sorted(campos)}"
    assert campos[FACET_NOMBRE]["type"] == "text"

    candidato = {"key": FACET_NOMBRE, "value": nombre, "exact": False}
    conteo = acceso_obj.get_search_counts_perdidos(
        location="", area="", status=ESTATUS_TODOS, locations=[LOCATION], facets=[], candidates=[candidato]
    )
    assert conteo == [1], f"El buscador cuenta {conteo} artículos con el nombre '{nombre}'"

    facets = [{"key": FACET_NOMBRE, "values": [nombre], "exact": False}]
    lista = acceso_obj.get_list_article_lost("", "", ESTATUS_TODOS, limit=LIMITE_LISTA, locations=[LOCATION], facets=facets)
    assert [a["folio"] for a in lista["records"]] == [articulo_pendiente["folio"]], (
        f"El buscador trae {[a['folio'] for a in lista['records']]}, se esperaba solo {articulo_pendiente['folio']}"
    )
