# coding: utf-8

"""
Tipo de equipo de la bitácora (_tipo_equipo_bitacora): el radio "Tipo de
equipo" solo acepta herramienta, computo, tablet y otra, y el pase trae el
tipo del catálogo de la cuenta. Función pura, sin red.
Notion: TB-259 y TB-260.
"""

import pytest

from ..data.equipos_data import (
    EQUIPO_VISITA,
    EQUIPO_AGREGADO,
    EQUIPO_TIPO_CATALOGO,
    TIPO_SINONIMO_CON_ACENTO,
    TIPO_FUERA_DEL_RADIO,
    NOMBRE_PROYECTOR,
)


@pytest.mark.unit
def test_tipo_valido_o_sinonimo_queda_como_opcion_de_la_bitacora(accesos_no_api):
    """
    TB-259: un tipo que ya es opción del radio debe quedar igual (en
    minúsculas) y un sinónimo del catálogo ("Laptop", "Computadora Portátil",
    con mayúsculas, acentos o espacios) debe convertirse a la opción del radio,
    sin tocar el nombre. Si no, LinkaForm rechaza la entrada con el equipo.
    """
    acc = accesos_no_api
    nombre = EQUIPO_VISITA["nombre"]

    assert acc._tipo_equipo_bitacora(EQUIPO_AGREGADO["tipo"], nombre) == ("herramienta", nombre)
    assert acc._tipo_equipo_bitacora(EQUIPO_TIPO_CATALOGO["tipo"], nombre) == ("computo", nombre)
    assert acc._tipo_equipo_bitacora(TIPO_SINONIMO_CON_ACENTO, nombre) == ("computo", nombre)


@pytest.mark.unit
def test_tipo_que_no_existe_en_la_bitacora_queda_como_otra(accesos_no_api):
    """
    TB-260: un tipo que no es opción del radio ni sinónimo debe guardarse
    como 'otra'; si el equipo no trae nombre, el tipo original pasa al nombre
    para no perderlo. Si trae nombre, se respeta. Si no, la entrada se
    rechaza o el guardia no sabe qué equipo era.
    """
    acc = accesos_no_api

    assert acc._tipo_equipo_bitacora(TIPO_FUERA_DEL_RADIO, "") == ("otra", TIPO_FUERA_DEL_RADIO)
    assert acc._tipo_equipo_bitacora(TIPO_FUERA_DEL_RADIO, NOMBRE_PROYECTOR) == ("otra", NOMBRE_PROYECTOR)
