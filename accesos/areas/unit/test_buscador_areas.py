# coding: utf-8

"""
Buscador y panel de filtros de Disponibles (get_search_counts_areas y
areas_details_match en Sanic) sin tocar la cuenta: se simula la consulta y se
revisa qué se pide.
Notion: TB-382 y TB-383.
"""

import pytest

from ..data.areas_data import (
    AREA,
    CANDIDATOS_BUSCADOR,
    FILTRO_SOLO_TAG,
    FILTRO_SOLO_QR,
    FILTRO_TAG_Y_QR,
)

pytestmark = pytest.mark.back("sanic")


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
