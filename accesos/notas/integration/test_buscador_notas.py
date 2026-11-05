# coding: utf-8

"""
Buscador de la lista de notas (get_search_fields_notas, get_search_counts_notas
y get_list_notes con facets, como notas/page.tsx).
Notion: TB-136 y TB-145.
"""

import pytest

from .fixtures import *
from ..data.notas_data import (
    LOCATION,
    AREA,
    TODAS_LAS_AREAS,
    ESTATUS_TODOS,
    LIMITE_LISTA,
    FACET_NOTA,
    FACET_CASETA,
)


@pytest.mark.integration
def test_buscador_de_notas_encuentra_la_nota_por_texto(acceso_obj, nota_texto_unico):
    """
    TB-136: el buscador ofrece el campo Nota y, al escribir el texto de una
    nota, la cuenta y la trae. Si no, el guardia no encuentra lo que dejó
    anotado otro turno.
    """
    nota_id, texto = nota_texto_unico

    campos = {c["key"]: c for c in acceso_obj.get_search_fields_notas()}
    assert FACET_NOTA in campos, f"El buscador no ofrece el campo '{FACET_NOTA}': {sorted(campos)}"
    assert campos[FACET_NOTA]["type"] == "text"

    candidato = {"key": FACET_NOTA, "value": texto, "exact": False}
    conteo = acceso_obj.get_search_counts_notas(
        location="", area="", status=ESTATUS_TODOS, locations=[LOCATION], facets=[], candidates=[candidato]
    )
    assert conteo == [1], f"El buscador cuenta {conteo} notas con el texto '{texto}'"

    facets = [{"key": FACET_NOTA, "values": [texto], "exact": False}]
    lista = acceso_obj.get_list_notes(LOCATION, TODAS_LAS_AREAS, status=ESTATUS_TODOS, limit=LIMITE_LISTA, facets=facets)
    assert [n["_id"] for n in lista["records"]] == [nota_id], (
        f"El buscador trae {[n['_id'] for n in lista['records']]}, se esperaba solo {nota_id}"
    )


@pytest.mark.integration
def test_buscador_de_notas_encuentra_la_nota_por_caseta(acceso_obj, nota_texto_unico):
    """
    TB-145: el buscador ofrece el campo Caseta y, junto con el texto de la
    nota, debe traerla al buscar por la caseta donde se creó. Si no, filtrar
    por caseta deja fuera las notas de esa caseta.
    """
    nota_id, texto = nota_texto_unico

    campos = {c["key"]: c for c in acceso_obj.get_search_fields_notas()}
    assert FACET_CASETA in campos, f"El buscador no ofrece el campo '{FACET_CASETA}': {sorted(campos)}"

    facets = [
        {"key": FACET_NOTA, "values": [texto], "exact": False},
        {"key": FACET_CASETA, "values": [AREA], "exact": False},
    ]
    lista = acceso_obj.get_list_notes(LOCATION, TODAS_LAS_AREAS, status=ESTATUS_TODOS, limit=LIMITE_LISTA, facets=facets)
    assert nota_id in {n["_id"] for n in lista["records"]}, f"Buscar por la caseta {AREA} no trae la nota"
