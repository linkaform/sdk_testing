# coding: utf-8

"""
Lista de notas (get_list_notes) sin tocar preprod: se simula la consulta a la
base (cr.aggregate) y se revisa el filtro del buscador y la paginación.
Notion: TB-172.
"""

import pytest

from ..data.notas_data import (
    LOCATION,
    TODAS_LAS_AREAS,
    ESTATUS_TODOS,
    FACET_NOTA,
    NOTA_NUEVA,
    NOTAS_EN_TOTAL,
    NOTAS_POR_PAGINA,
    SALTAR_NOTAS,
)


@pytest.mark.unit
def test_lista_de_notas_aplica_el_buscador_y_pagina(accesos_no_api, mocker):
    """
    TB-172: con un filtro del buscador, 10 por página y saltando 10, la
    consulta debe llevar la condición del buscador, saltar 10 y traer 10, y
    la respuesta debe decir página 2 de 3 con 25 notas. Si no, el buscador no
    filtra o la paginación repite o salta notas.
    """
    nota = {"_id": "6650a1b2c3d4e5f6a7b8c9d0", "note": NOTA_NUEVA["note"]}
    consulta = mocker.patch.object(
        accesos_no_api.cr, "aggregate", side_effect=[[dict(nota)], [{"total": NOTAS_EN_TOTAL}]]
    )
    facets = [{"key": FACET_NOTA, "values": [NOTA_NUEVA["note"]], "exact": False}]

    lista = accesos_no_api.get_list_notes(
        LOCATION, TODAS_LAS_AREAS, status=ESTATUS_TODOS, limit=NOTAS_POR_PAGINA, offset=SALTAR_NOTAS, facets=facets
    )

    pasos = consulta.call_args_list[0].args[0]
    match = pasos[0]["$match"]
    assert match.get("$and"), f"La consulta no lleva la condición del buscador: {match}"
    assert {"$skip": SALTAR_NOTAS} in pasos, f"La consulta no salta {SALTAR_NOTAS}: {pasos}"
    assert {"$limit": NOTAS_POR_PAGINA} in pasos, f"La consulta no trae {NOTAS_POR_PAGINA}: {pasos}"
    assert lista["total_records"] == NOTAS_EN_TOTAL
    assert lista["actual_page"] == 2, f"Página {lista['actual_page']}"
    assert lista["total_pages"] == 3, f"Total de páginas {lista['total_pages']}"
    assert len(lista["records"]) == 1
