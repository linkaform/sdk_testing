# coding: utf-8

"""
Equipos de la entrada y del pase: cómo se arman los grupos de equipos que se
guardan (_answers_equipos, _answers_equipos_pase) y cómo se leen
(format_equipos_simple). Funciones puras, sin red.
Notion: TB-261 a TB-263.
"""

import pytest

from ..data.equipos_data import EQUIPO_VISITA, EQUIPO_TIPO_CATALOGO, RENGLON_VACIO


@pytest.mark.bug(1565)
def test_equipo_con_llaves_de_id_regresa_su_modelo_no_su_marca(accesos_no_api):
    """
    TB-263: un equipo que llega con los ids de los campos debe leerse con su
    modelo en 'modelo' y su marca en 'marca'. format_equipos_simple lo usa
    para la entrada de los acompañantes (_data_acompanante); si regresa la
    marca como modelo, la bitácora guarda el equipo con datos cruzados
    (ticket 2610-1565).
    """
    acc = accesos_no_api
    mf = acc.mf
    con_ids = {
        mf["nombre_articulo"]: EQUIPO_VISITA["nombre"],
        mf["marca_articulo"]: EQUIPO_VISITA["marca"],
        mf["modelo_articulo"]: EQUIPO_VISITA["modelo"],
        mf["numero_serie"]: EQUIPO_VISITA["serie"],
    }

    leido = acc.format_equipos_simple([con_ids])[0]

    assert leido["marca"] == EQUIPO_VISITA["marca"], f"La marca quedó {leido['marca']!r}"
    assert leido["modelo"] == EQUIPO_VISITA["modelo"], f"El modelo quedó {leido['modelo']!r}"
