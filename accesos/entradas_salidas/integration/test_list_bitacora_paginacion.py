# coding: utf-8

"""
Lista de la bitácora (list_bitacora2 → get_list_bitacora): paginación,
búsqueda por facets y desglose de vehículos/equipos.
Notion: TB-051 a TB-054.
"""

import pytest
from math import ceil

from .fixtures import *
from ..data.bitacora_data import (
    LOCATION, AREA, LIMITE_LISTA, VEHICULOS_DESGLOSE, EQUIPO_PRUEBA, FACETS_BUSQUEDA,
)
from .helpers import ultima_visita, salida_silenciosa

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


@pytest.mark.integration
def test_list_bitacora_busqueda_por_facets(acceso_obj, pase_dentro):
    """
    TB-053: el buscador de la bitácora usa facets {key, values, exact}. Sin
    exact busca "contiene" ignorando mayúsculas y acentos; con exact, el valor
    completo; varios facets se combinan con AND. get_search_fields regresa
    los 7 campos del buscador.
    """
    folio_pase, _ = pase_dentro
    visita = ultima_visita(acceso_obj, folio_pase)

    # "Contiene", con otra combinación de mayúsculas y acentos que el nombre guardado.
    por_nombre = acceso_obj.get_list_bitacora(
        location=LOCATION, area=AREA, facets=FACETS_BUSQUEDA["por_nombre"], limit=LIMITE_LISTA,
    )["records"]
    assert visita["_id"] in {r["_id"] for r in por_nombre}, "La búsqueda por nombre no encontró la visita"

    # Valor completo del folio.
    por_folio = acceso_obj.get_list_bitacora(
        location=LOCATION, area=AREA, facets=[{"key": "folio", "values": [visita["folio"]], "exact": True}],
        limit=LIMITE_LISTA,
    )["records"]
    assert visita["_id"] in {r["_id"] for r in por_folio}, "La búsqueda exacta por folio no encontró la visita"
    assert all(r["folio"] == visita["folio"] for r in por_folio), "La búsqueda exacta por folio trajo otros folios"

    # AND: el nombre coincide pero el estatus no (la visita sigue en entrada).
    combinados = acceso_obj.get_list_bitacora(
        location=LOCATION, area=AREA, facets=FACETS_BUSQUEDA["nombre_y_salida"], limit=LIMITE_LISTA,
    )["records"]
    assert visita["_id"] not in {r["_id"] for r in combinados}, "Los facets no se combinaron con AND"
    assert all(r["status_visita"] == "Salida" for r in combinados)

    campos = {c["key"]: c for c in acceso_obj.get_search_fields_bitacora()}
    assert set(campos) == {
        "folio", "nombre_visitante", "contratista", "status", "perfil_visita", "visita_a", "caseta",
    }, f"Campos del buscador inesperados: {sorted(campos)}"
    assert campos["status"]["type"] == "enum"
    assert {"entrada", "salida"} <= {o["value"] for o in campos["status"]["options"]}


@pytest.mark.integration
def test_list_bitacora_desglose_de_vehiculos_y_equipos(acceso_obj, pase_activo):
    """
    TB-054: con desglose='vehiculos' o 'equipos' la lista regresa una fila por
    cada vehículo/equipo de la visita (pestañas de Bitácoras) y la paginación
    cuenta esas filas; sin desglose, la visita es una sola fila.
    El folio no es único en preprod (el consecutivo se ha repetido), así que
    la búsqueda por folio puede traer otras visitas: se revisan solo las filas
    de esta visita y que el total cuadre con las filas regresadas.
    """
    res = acceso_obj.do_access(
        pase_activo, LOCATION, AREA, {"vehiculo": VEHICULOS_DESGLOSE, "equipo": [EQUIPO_PRUEBA]}
    )
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada con vehículos: {res}"

    try:
        visita = ultima_visita(acceso_obj, pase_activo)
        por_folio = [{"key": "folio", "values": [visita["folio"]], "exact": True}]

        vehiculos = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, facets=por_folio, desglose="vehiculos", limit=LIMITE_LISTA,
        )
        filas_vehiculos = [r for r in vehiculos["records"] if r["_id"] == visita["_id"]]
        assert vehiculos["total_records"] == len(vehiculos["records"]), "El total no cuenta una fila por vehículo"
        assert len(filas_vehiculos) == len(VEHICULOS_DESGLOSE), f"Filas de la visita: {len(filas_vehiculos)}"
        placas = {v.get("placas") for r in filas_vehiculos for v in r["vehiculos"]}
        assert placas == {v["placas"] for v in VEHICULOS_DESGLOSE}, f"Placas inesperadas en el desglose: {placas}"

        equipos = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, facets=por_folio, desglose="equipos", limit=LIMITE_LISTA,
        )
        filas_equipos = [r for r in equipos["records"] if r["_id"] == visita["_id"]]
        assert equipos["total_records"] == len(equipos["records"]), "El total no cuenta una fila por equipo"
        assert len(filas_equipos) == 1, f"Filas de la visita: {len(filas_equipos)}"

        sin_desglose = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, facets=por_folio, desglose="", limit=LIMITE_LISTA,
        )
        filas_visita = [r for r in sin_desglose["records"] if r["_id"] == visita["_id"]]
        assert sin_desglose["total_records"] == len(sin_desglose["records"])
        assert len(filas_visita) == 1, f"Sin desglose la visita debe ser una sola fila: {len(filas_visita)}"
        assert len(filas_visita[0]["vehiculos"]) == len(VEHICULOS_DESGLOSE)
    finally:
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)
