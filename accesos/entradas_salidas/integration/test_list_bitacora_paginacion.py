# coding: utf-8

"""
Lista de la bitácora (list_bitacora2 → get_list_bitacora): paginación,
búsqueda por facets y desglose de vehículos/equipos.
Notion: TB-051 a TB-054.
"""

import pytest
from math import ceil

from .fixtures import *
from ..data.bitacora_data import LOCATION, AREA

# Página chica para que la lista de preprod tenga varias páginas.
POR_PAGINA = 5


@pytest.mark.integration
def test_list_bitacora_paginacion_coherente(acceso_obj, pase_dentro):
    """
    TB-051: los datos de paginación (total_records, total_pages, actual_page,
    records_on_page) deben cuadrar con los registros que regresa cada página;
    una página fuera de rango regresa vacía pero con el total correcto.
    """
    primera = acceso_obj.get_list_bitacora(location=LOCATION, area=AREA, limit=POR_PAGINA, offset=0)
    total = primera["total_records"]

    assert total >= 1, "La bitácora de la ubicación viene vacía aunque hay una entrada abierta"
    assert primera["total_pages"] == ceil(total / POR_PAGINA)
    assert primera["actual_page"] == 1
    assert primera["records_on_page"] == len(primera["records"]) == min(POR_PAGINA, total)

    if total > POR_PAGINA:
        segunda = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, limit=POR_PAGINA, offset=POR_PAGINA,
        )
        assert segunda["actual_page"] == 2
        assert segunda["records_on_page"] == len(segunda["records"])
        ids_primera = {r["_id"] for r in primera["records"]}
        ids_segunda = {r["_id"] for r in segunda["records"]}
        assert not ids_primera & ids_segunda, "La página 2 repite registros de la página 1"

    fuera = acceso_obj.get_list_bitacora(
        location=LOCATION, area=AREA, limit=POR_PAGINA, offset=total + POR_PAGINA,
    )
    assert fuera["records"] == [], "Una página fuera de rango debería venir vacía"
    assert fuera["records_on_page"] == 0
    assert fuera["total_records"] == total, "El total cambió en la página fuera de rango"


@pytest.mark.integration
@pytest.mark.parametrize("limit, offset", [
    (0, 0),
    (POR_PAGINA, -1),
    ("5", "0"),
], ids=["limit_cero", "offset_negativo", "valores_texto"])
def test_list_bitacora_paginacion_invalida_responde_error_controlado(acceso_obj, limit, offset):
    """
    TB-052: limit/offset inválidos deben responder un error de validación del
    sistema (status_code 400), no una excepción interna de Mongo o de Python.
    El front siempre manda valores válidos; esto protege llamadas directas.
    """
    with pytest.raises(Exception) as exc_info:
        acceso_obj.get_list_bitacora(location=LOCATION, area=AREA, limit=limit, offset=offset)

    error = exc_info.value
    assert type(error) is Exception and '"status_code": 400' in str(error), (
        f"Error no controlado ({type(error).__name__}): {error}"
    )
