# coding: utf-8

"""
Vehículos de la entrada y del pase: cómo se arman los grupos de vehículos
que se guardan (_answers_vehiculos, _answers_vehiculos_pase) y cómo se leen
(format_vehiculos_simple). Funciones puras, sin red.
Notion: TB-254 a TB-256.
"""

import pytest
from lkf_back import de

from ..data.vehiculos_data import VEHICULO_VISITA, VEHICULO_LLAVES_LARGAS, RENGLON_VACIO


@pytest.mark.unit
def test_vehiculos_de_la_entrada_se_guardan_en_el_grupo_de_la_bitacora(accesos_no_api):
    """
    TB-254: _answers_vehiculos debe guardar tipo, marca y modelo en el
    catálogo de vehículos, el estado en su catálogo y placas, color y foto
    en sus campos; los renglones vacíos se omiten. Si un dato cae fuera de
    su campo, la pestaña Vehículos no lo muestra.
    """
    acc = accesos_no_api
    mf = acc.mf

    grupo = acc._answers_vehiculos([VEHICULO_VISITA, RENGLON_VACIO, None])

    assert len(grupo) == 1, f"Se armaron {len(grupo)} vehículos, se mandó 1 con datos"
    vehiculo = grupo[0]
    assert vehiculo[de(acc, "TIPO_DE_VEHICULO_OBJ_ID").TIPO_DE_VEHICULO_OBJ_ID] == {
        mf["tipo_vehiculo"]: VEHICULO_VISITA["tipo"],
        mf["marca_vehiculo"]: VEHICULO_VISITA["marca"],
        mf["modelo_vehiculo"]: VEHICULO_VISITA["modelo"],
    }
    assert vehiculo[acc.ESTADO_OBJ_ID] == {mf["nombre_estado"]: VEHICULO_VISITA["estado"]}
    assert vehiculo[mf["placas_vehiculo"]] == VEHICULO_VISITA["placas"]
    assert vehiculo[mf["color_vehiculo"]] == VEHICULO_VISITA["color"]
    assert vehiculo[mf["foto_vehiculo"]] == []


@pytest.mark.unit
def test_vehiculos_del_pase_se_guardan_con_llaves_cortas_o_largas(accesos_no_api):
    """
    TB-255: el front manda los vehículos del pase con llaves cortas (tipo,
    placas…) y otros flujos con las largas (tipo_vehiculo, placas_vehiculo…).
    _answers_vehiculos_pase debe armar el mismo grupo con las dos. Si una
    forma se pierde, el pase se guarda con el vehículo vacío.
    """
    acc = accesos_no_api

    cortas = acc._answers_vehiculos_pase([VEHICULO_VISITA])
    largas = acc._answers_vehiculos_pase([VEHICULO_LLAVES_LARGAS])

    assert cortas == largas, f"Con llaves cortas quedó {cortas}, con largas {largas}"
    assert cortas[0][acc.mf["placas_vehiculo"]] == VEHICULO_VISITA["placas"]
    assert cortas[0][de(acc, "TIPO_DE_VEHICULO_OBJ_ID").TIPO_DE_VEHICULO_OBJ_ID][acc.mf["tipo_vehiculo"]] == VEHICULO_VISITA["tipo"]


@pytest.mark.unit
def test_vehiculos_se_leen_igual_en_cualquiera_de_sus_formatos(accesos_no_api):
    """
    TB-256: un vehículo puede llegar con las etiquetas de la lista
    (placas_vehiculo), con las llaves cortas del front (placas) o con los ids
    de los campos. format_vehiculos_simple debe regresar las mismas placas,
    tipo y color en los tres casos. Si no, el acompañante entra sin los datos
    de su vehículo.
    """
    acc = accesos_no_api
    mf = acc.mf
    con_ids = {
        mf["placas_vehiculo"]: VEHICULO_VISITA["placas"],
        mf["tipo_vehiculo"]: VEHICULO_VISITA["tipo"],
        mf["color_vehiculo"]: VEHICULO_VISITA["color"],
    }

    for formato in (VEHICULO_LLAVES_LARGAS, VEHICULO_VISITA, con_ids):
        leido = acc.format_vehiculos_simple([formato])[0]
        assert leido["placas"] == VEHICULO_VISITA["placas"], f"Placas {leido['placas']!r} desde {formato}"
        assert leido["tipo"] == VEHICULO_VISITA["tipo"], f"Tipo {leido['tipo']!r} desde {formato}"
        assert leido["color"] == VEHICULO_VISITA["color"], f"Color {leido['color']!r} desde {formato}"
