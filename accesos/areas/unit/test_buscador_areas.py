# coding: utf-8

"""
Buscador y panel de filtros de Disponibles (get_search_counts_areas y
areas_details_match en Sanic) sin tocar la cuenta: se simula la consulta y se
revisa qué se pide.
Notion: TB-381 a TB-383.
"""

import pytest

from ..data.areas_data import (
    LOCATION,
    AREA,
    CANDIDATOS_BUSCADOR,
    FILTRO_SOLO_TAG,
    FILTRO_SOLO_QR,
    FILTRO_TAG_Y_QR,
)

pytestmark = pytest.mark.back("sanic")


@pytest.mark.unit
@pytest.mark.target("get_search_counts_areas")
def test_conteos_del_buscador_no_cuentan_areas_homonimas_de_otra_ubicacion(accesos_no_api, mocker):
    """
    TB-381: los chips del buscador cuentan las áreas de las ubicaciones
    elegidas. La consulta se arma con los nombres de esas áreas; si no filtra
    también por la ubicación, un área con el mismo nombre en otra ubicación
    suma en los conteos (lo mismo que TB-343 en la lista).
    """
    acc = accesos_no_api
    mocker.patch.object(acc, "areas_de_ubicaciones", return_value=[AREA])
    cr = mocker.MagicMock()
    cr.aggregate.return_value = []
    mocker.patch.object(acc, "cr", cr, create=True)

    acc.get_search_counts_areas(locations=[LOCATION], candidates=[dict(c) for c in CANDIDATOS_BUSCADOR])

    consulta = cr.aggregate.call_args.args[0]
    assert LOCATION in str(consulta), f"La consulta de los conteos no filtra por {LOCATION}: {consulta}"


@pytest.mark.unit
@pytest.mark.target("get_search_counts_areas")
def test_conteos_del_buscador_sin_ubicaciones_regresan_ceros_sin_consultar(accesos_no_api, mocker):
    """
    TB-382: sin ubicación elegida no hay áreas que contar. Cada chip debe
    mostrar 0 sin buscar áreas ni consultar la base; si consulta, contaría
    las áreas de todas las ubicaciones.
    """
    acc = accesos_no_api
    buscar = mocker.patch.object(acc, "areas_de_ubicaciones", return_value=[AREA])
    cr = mocker.MagicMock()
    mocker.patch.object(acc, "cr", cr, create=True)

    conteos = acc.get_search_counts_areas(locations=[], candidates=[dict(c) for c in CANDIDATOS_BUSCADOR])

    assert conteos == [0, 0]
    buscar.assert_not_called()
    cr.aggregate.assert_not_called()


@pytest.mark.unit
@pytest.mark.target("areas_details_match")
def test_filtro_tag_qr_del_panel_arma_la_condicion_correcta(accesos_no_api):
    """
    TB-383: en el panel de filtros, "Tag" debe traer solo las áreas con tag
    capturado y "QR" solo las que no lo tienen (se checan por el QR de su
    registro). Con las dos opciones marcadas no se filtra.
    """
    acc = accesos_no_api
    tag = f"answers.{acc.f['area_tag_id']}"

    solo_tag = acc.areas_details_match([AREA], [dict(f) for f in FILTRO_SOLO_TAG])
    solo_qr = acc.areas_details_match([AREA], [dict(f) for f in FILTRO_SOLO_QR])
    ambos = acc.areas_details_match([AREA], [dict(f) for f in FILTRO_TAG_Y_QR])

    assert solo_tag[tag] == {"$exists": True, "$nin": [None, "", []]}
    assert solo_qr[tag] == {"$in": [None, "", []]}
    assert tag not in ambos, f"Tag y QR juntos filtran: {ambos[tag]}"
