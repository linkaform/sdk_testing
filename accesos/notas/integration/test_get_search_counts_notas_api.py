# coding: utf-8

"""
Conteos del buscador de notas (get_search_counts_notas) contra la lista
(get_list_notes): el número junto a cada opción debe ser lo que trae la lista
al hacer clic. Solo lectura: no crea, edita ni borra notas.
Notion: TB-188 a TB-191.
"""

import pytest

from .fixtures import *
from ..data.notas_data import (
    LOCATION,
    AREA,
    TODAS_LAS_AREAS,
    ESTATUS_TODOS,
    ESTATUS_ABIERTO,
    ESTATUS_CERRADO,
    FACET_ESTATUS,
    FACET_NOTA,
    TEXTO_BUSCADOR_LARGO,
)


def _total_lista(acceso_obj, area, locations, facets):
    """Total de registros que trae la lista con esos filtros (lo que ve el guardia al hacer clic)."""
    res = acceso_obj.get_list_notes(
        LOCATION, area, status=ESTATUS_TODOS, limit=1, locations=locations, facets=facets
    )
    return res["total_records"]


@pytest.mark.integration
@pytest.mark.bug(1552)
def test_get_search_counts_notas_candidato_de_la_misma_llave_cuenta_como_or(acceso_obj):
    """
    TB-188: con el chip Estatus=abierto puesto, la opción "cerrado" debe
    mostrar cuántas notas trae la lista al agregarla. FacetSearch.tsx mete el
    valor en el mismo facet (OR), pero count_facet_candidates lo cuenta como
    un facet aparte (AND), así que muestra 0 aunque al hacer clic salgan todas.
    """
    facets = [{"key": FACET_ESTATUS, "values": [ESTATUS_ABIERTO], "exact": True}]
    candidato = {"key": FACET_ESTATUS, "value": ESTATUS_CERRADO, "exact": True}

    conteo = acceso_obj.get_search_counts_notas(
        "", "", status=ESTATUS_TODOS, locations=[LOCATION], facets=facets, candidates=[candidato]
    )
    al_hacer_clic = _total_lista(
        acceso_obj, TODAS_LAS_AREAS, [LOCATION],
        [{"key": FACET_ESTATUS, "values": [ESTATUS_ABIERTO, ESTATUS_CERRADO], "exact": True}],
    )
    assert conteo == [al_hacer_clic], (
        f"La opción '{ESTATUS_CERRADO}' muestra {conteo} y al hacer clic la lista trae {al_hacer_clic}"
    )


@pytest.mark.integration
@pytest.mark.bug(1552)
def test_get_search_counts_notas_respeta_el_area_de_la_caseta(acceso_obj):
    """
    TB-189: la lista de notas se pide con el área de la caseta; el conteo del
    buscador debe contar sobre las mismas notas. getSearchCounts
    (facet-search.ts) no manda área, así que cuenta notas de todas las casetas
    y el número no coincide con lo que sale al hacer clic.
    """
    candidato = {"key": FACET_ESTATUS, "value": ESTATUS_ABIERTO, "exact": True}
    # Payload de getSearchCounts tal como lo manda el front: location "" y sin área.
    conteo = acceso_obj.get_search_counts_notas(
        "", "", status=ESTATUS_TODOS, locations=[LOCATION], candidates=[candidato]
    )
    al_hacer_clic = _total_lista(
        acceso_obj, AREA, [LOCATION],
        [{"key": FACET_ESTATUS, "values": [ESTATUS_ABIERTO], "exact": True}],
    )
    assert conteo == [al_hacer_clic], (
        f"En {AREA} el conteo de '{ESTATUS_ABIERTO}' es {conteo} y la lista trae {al_hacer_clic}"
    )


@pytest.mark.integration
@pytest.mark.bug(1552)
def test_get_search_counts_notas_sin_ubicaciones_del_header_usa_la_de_la_caseta(acceso_obj):
    """
    TB-190: sin ubicaciones elegidas en el header (selectedLocations = [], así
    arranca el store), la lista filtra por la ubicación de la caseta, pero el
    conteo queda con answers.AREAS.L == "" y da 0 en todas las opciones.
    """
    candidato = {"key": FACET_ESTATUS, "value": ESTATUS_ABIERTO, "exact": True}
    # Payload de getSearchCounts tal como lo manda el front: location "" y sin área.
    conteo = acceso_obj.get_search_counts_notas(
        "", "", status=ESTATUS_TODOS, locations=[], candidates=[candidato]
    )
    al_hacer_clic = _total_lista(
        acceso_obj, AREA, [],
        [{"key": FACET_ESTATUS, "values": [ESTATUS_ABIERTO], "exact": True}],
    )
    assert al_hacer_clic > 0, f"No hay notas '{ESTATUS_ABIERTO}' en {LOCATION}/{AREA} para comparar"
    assert conteo == [al_hacer_clic], (
        f"Sin ubicaciones en el header el conteo es {conteo} y la lista trae {al_hacer_clic}"
    )


@pytest.mark.integration
@pytest.mark.bug(1552)
def test_get_search_counts_notas_texto_largo_no_truena(acceso_obj):
    """
    TB-191: un texto de 2000 letras en el buscador se expande a una regex de
    ~40 KB, arriba del límite de Mongo (code 51091 "regular expression is too
    large"). El buscador debe recortar o validar el texto en vez de tronar.
    """
    candidato = {"key": FACET_NOTA, "value": TEXTO_BUSCADOR_LARGO, "exact": False}
    conteo = acceso_obj.get_search_counts_notas(
        "", "", status=ESTATUS_TODOS, locations=[LOCATION], candidates=[candidato]
    )
    assert isinstance(conteo, list) and len(conteo) == 1, f"Respuesta inesperada: {conteo}"
