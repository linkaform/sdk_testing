# coding: utf-8

"""
Lista de la pestaña Vehículos de Bitácoras: get_list_bitacora con
desglose='vehiculos' (una fila por vehículo), opciones Dentro y Todos.
Notion: TB-095 a TB-098.
"""

from math import ceil

import pytest

from .fixtures import *
from ..data.vehiculos_data import (
    LOCATION,
    AREA,
    LIMITE_LISTA,
    DESGLOSE_VEHICULOS,
    FILTRO_DENTRO,
    VEHICULO_VISITA,
    VEHICULOS_VISITA_DOS,
    FILAS_POR_PAGINA,
    VEHICULO_AGREGADO,
)
from entradas_salidas.integration.helpers import ultima_visita, salida_silenciosa, dar_entrada


@pytest.mark.integration
def test_vehiculos_dentro_solo_trae_visitas_abiertas(acceso_obj, pase_activo):
    """
    TB-095: Vehículos → Dentro debe traer solo vehículos de visitas abiertas
    (status Entrada), una fila por vehículo, e incluir el vehículo de la
    visita recién registrada. Si no, el guardia no ve qué vehículos siguen
    dentro de la ubicación.
    """
    res = acceso_obj.do_access(pase_activo, LOCATION, AREA, {"vehiculo": [VEHICULO_VISITA]})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada con vehículo: {res}"

    try:
        visita = ultima_visita(acceso_obj, pase_activo)

        dentro = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, dynamic_filters=FILTRO_DENTRO,
            desglose=DESGLOSE_VEHICULOS, limit=LIMITE_LISTA,
        )
        filas = dentro["records"]

        assert filas, "Vehículos Dentro viene vacío"
        assert all(r["status_visita"] == "Entrada" for r in filas), (
            f"Vehículos Dentro trae otros estatus: {sorted({r['status_visita'] for r in filas})}"
        )
        assert all(len(r["vehiculos"]) == 1 for r in filas), "Hay filas con más de un vehículo (no se desglosó)"

        filas_visita = [r for r in filas if r["_id"] == visita["_id"]]
        assert len(filas_visita) == 1, f"La visita debe ser una fila (un vehículo): {len(filas_visita)}"
        assert filas_visita[0]["vehiculos"][0]["placas"] == VEHICULO_VISITA["placas"]
    finally:
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)


@pytest.mark.integration
def test_vehiculo_tras_la_salida_sale_de_dentro_y_sigue_en_todos(acceso_obj, pase_activo):
    """
    TB-096: después de registrar la salida, el vehículo de la visita ya no
    debe salir en Vehículos → Dentro, pero sí en Vehículos → Todos con status
    Salida. Si sigue en Dentro, el guardia cree que el vehículo no ha salido.
    """
    res = acceso_obj.do_access(pase_activo, LOCATION, AREA, {"vehiculo": [VEHICULO_VISITA]})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada con vehículo: {res}"
    visita = ultima_visita(acceso_obj, pase_activo)

    try:
        acceso_obj.do_out(pase_activo, LOCATION, AREA)

        dentro = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, dynamic_filters=FILTRO_DENTRO,
            desglose=DESGLOSE_VEHICULOS, limit=LIMITE_LISTA,
        )
        assert visita["_id"] not in {r["_id"] for r in dentro["records"]}, "El vehículo sigue en Dentro después de la salida"

        todos = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, desglose=DESGLOSE_VEHICULOS, limit=LIMITE_LISTA,
        )
        filas_visita = [r for r in todos["records"] if r["_id"] == visita["_id"]]
        assert len(filas_visita) == 1, f"El vehículo no aparece en Todos: {len(filas_visita)} filas"
        assert filas_visita[0]["status_visita"] == "Salida", f"En Todos quedó '{filas_visita[0]['status_visita']}'"
        assert filas_visita[0]["vehiculos"][0]["placas"] == VEHICULO_VISITA["placas"]
    finally:
        # Si do_out falló, cierra la visita para no dejarla abierta en preprod.
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)


@pytest.mark.integration
def test_paginacion_de_vehiculos_no_repite_ni_pierde(acceso_obj, pase_activo):
    """
    TB-097: con el desglose, la paginación cuenta filas de vehículo. Al
    recorrer de una fila por página, los 2 vehículos de una visita deben
    salir una vez cada uno, y total_pages/actual_page deben cuadrar con el
    total. Si se repite o se pierde un vehículo al cambiar de página, el
    guardia no ve todos los vehículos que entraron.
    """
    res = acceso_obj.do_access(pase_activo, LOCATION, AREA, {"vehiculo": VEHICULOS_VISITA_DOS})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada con vehículos: {res}"

    try:
        visita = ultima_visita(acceso_obj, pase_activo)
        # El folio no es único en preprod: se revisan solo las filas de esta visita.
        por_folio = [{"key": "folio", "values": [visita["folio"]], "exact": True}]

        primera = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, facets=por_folio,
            desglose=DESGLOSE_VEHICULOS, limit=FILAS_POR_PAGINA, offset=0,
        )
        total = primera["total_records"]
        assert primera["total_pages"] == ceil(total / FILAS_POR_PAGINA)

        filas = []
        for pagina in range(primera["total_pages"]):
            res_pagina = acceso_obj.get_list_bitacora(
                location=LOCATION, area=AREA, facets=por_folio,
                desglose=DESGLOSE_VEHICULOS, limit=FILAS_POR_PAGINA, offset=pagina * FILAS_POR_PAGINA,
            )
            assert res_pagina["actual_page"] == pagina + 1, f"Página {pagina + 1} reporta {res_pagina['actual_page']}"
            assert res_pagina["records_on_page"] == len(res_pagina["records"]) <= FILAS_POR_PAGINA
            filas.extend(res_pagina["records"])

        assert len(filas) == total, f"Recorriendo las páginas salen {len(filas)} filas y el total dice {total}"
        placas_visita = [r["vehiculos"][0]["placas"] for r in filas if r["_id"] == visita["_id"]]
        assert sorted(placas_visita) == sorted(v["placas"] for v in VEHICULOS_VISITA_DOS), (
            f"Vehículos de la visita al recorrer las páginas: {placas_visita}"
        )
    finally:
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)


@pytest.mark.integration
def test_agregar_vehiculo_a_visita_abierta_aparece_en_dentro(acceso_obj, pase_activo):
    """
    TB-098: a una visita abierta sin vehículo, el guardia le agrega uno desde
    el modal "Nuevo Vehículo" (update_bitacora_entrada sin action). Debe
    aparecer como fila en Vehículos → Dentro con su placa; si no, el vehículo
    queda dentro sin que nadie lo vea en la lista.
    """
    visita = dar_entrada(acceso_obj, pase_activo, LOCATION, AREA)

    try:
        acceso_obj.update_bitacora_entrada({"vehiculo": VEHICULO_AGREGADO}, record_id=visita["_id"])

        dentro = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, dynamic_filters=FILTRO_DENTRO,
            desglose=DESGLOSE_VEHICULOS, limit=LIMITE_LISTA,
        )
        filas_visita = [r for r in dentro["records"] if r["_id"] == visita["_id"]]
        assert len(filas_visita) == 1, f"El vehículo agregado no aparece en Dentro: {len(filas_visita)} filas"
        assert filas_visita[0]["vehiculos"][0]["placas"] == VEHICULO_AGREGADO["placas"]
    finally:
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)
