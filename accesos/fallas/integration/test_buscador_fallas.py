# coding: utf-8

"""
Buscador de la lista de fallas (get_search_fields_fallas,
get_search_counts_fallas y get_list_fallas con facets, como el front).
Notion: TB-144.
"""

import pytest

from .fixtures import *
from ..data.fallas_data import (
    LOCATION,
    ESTATUS_TODOS,
    FACET_COMENTARIOS,
    LIMITE_LISTA,
)


@pytest.mark.integration
def test_buscador_de_fallas_encuentra_la_falla(acceso_obj, falla_abierta):
    """
    TB-144: el buscador ofrece el campo Comentarios y, al escribir el
    comentario de una falla, la cuenta y la trae. Si no, el guardia no
    encuentra la falla que reportó otro turno.
    """
    comentario = falla_abierta["falla_comentarios"]

    campos = {c["key"]: c for c in acceso_obj.get_search_fields_fallas()}
    assert FACET_COMENTARIOS in campos, f"El buscador no ofrece el campo '{FACET_COMENTARIOS}': {sorted(campos)}"
    assert campos[FACET_COMENTARIOS]["type"] == "text"

    candidato = {"key": FACET_COMENTARIOS, "value": comentario, "exact": False}
    conteo = acceso_obj.get_search_counts_fallas([LOCATION], "", status=ESTATUS_TODOS, facets=[], candidates=[candidato])
    assert conteo == [1], f"El buscador cuenta {conteo} fallas con el comentario '{comentario}'"

    facets = [{"key": FACET_COMENTARIOS, "values": [comentario], "exact": False}]
    lista = acceso_obj.get_list_fallas([LOCATION], "", status=ESTATUS_TODOS, limit=LIMITE_LISTA, facets=facets)
    assert [f["folio"] for f in lista["records"]] == [falla_abierta["folio"]], (
        f"El buscador trae {[f['folio'] for f in lista['records']]}, se esperaba solo {falla_abierta['folio']}"
    )
