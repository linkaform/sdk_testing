# coding: utf-8

"""
Equipos de la entrada y del pase: cómo se arman los grupos de equipos que se
guardan (_answers_equipos, _answers_equipos_pase) y cómo se leen
(format_equipos_simple). Funciones puras, sin red.
Notion: TB-261 a TB-263.
"""

import pytest

from ..data.equipos_data import EQUIPO_TIPO_CATALOGO, RENGLON_VACIO


@pytest.mark.unit
def test_equipos_de_la_entrada_se_guardan_con_el_tipo_de_la_bitacora(accesos_no_api):
    """
    TB-261: _answers_equipos debe guardar cada equipo con el tipo ya
    convertido a la opción del radio y el nombre, marca, modelo, color y
    serie en sus campos; los renglones vacíos se omiten. Si el tipo va sin
    convertir, LinkaForm rechaza la entrada.
    """
    acc = accesos_no_api
    mf = acc.mf

    grupo = acc._answers_equipos([EQUIPO_TIPO_CATALOGO, RENGLON_VACIO, None])

    assert len(grupo) == 1, f"Se armaron {len(grupo)} equipos, se mandó 1 con datos"
    equipo = grupo[0]
    assert equipo[mf["tipo_equipo"]] == "computo", f"El tipo quedó {equipo[mf['tipo_equipo']]!r}"
    assert equipo[mf["nombre_articulo"]] == EQUIPO_TIPO_CATALOGO["nombre"]
    assert equipo[mf["marca_articulo"]] == EQUIPO_TIPO_CATALOGO["marca"]
    assert equipo[mf["modelo_articulo"]] == EQUIPO_TIPO_CATALOGO["modelo"]
    assert equipo[mf["color_articulo"]] == EQUIPO_TIPO_CATALOGO["color"]
    assert equipo[mf["numero_serie"]] == EQUIPO_TIPO_CATALOGO["serie"]
