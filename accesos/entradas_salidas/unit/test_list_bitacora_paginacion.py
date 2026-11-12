# coding: utf-8

"""
Paginación de la lista de Entradas & Salidas (get_list_bitacora): se simula
la consulta a Mongo y se revisa qué se pide y qué se regresa.
Notion: TB-267 y TB-268.
"""

import pytest

from ..data.bitacora_data import LOCATION, AREA, POR_PAGINA, TOTAL_REGISTROS, OFFSET_PAGINA_2, PAGINAS_ESPERADAS


def mongo_simulado(acceso_obj, mocker, respuestas):
    """Reemplaza la conexión a Mongo; cada llamada a aggregate regresa la siguiente respuesta."""
    cr = mocker.MagicMock()
    cr.aggregate.side_effect = respuestas
    mocker.patch.object(acceso_obj, "cr", cr, create=True)
    return cr


@pytest.mark.unit
def test_paginacion_invalida_se_rechaza_sin_consultar(accesos_no_api, mocker):
    """
    TB-267: limit y offset deben ser enteros (limit mayor a 0, offset 0 o
    más). Con texto, cero, negativos o True, get_list_bitacora debe detenerse
    con "Paginación inválida" y no consultar Mongo. Si consulta, Mongo
    truena con un error que el guardia no entiende.
    """
    cr = mongo_simulado(accesos_no_api, mocker, [])

    for limit, offset in ((str(POR_PAGINA), 0), (0, 0), (POR_PAGINA, -1), (True, 0)):
        with pytest.raises(Exception, match="Paginaci"):
            accesos_no_api.get_list_bitacora(LOCATION, AREA, limit=limit, offset=offset)
    cr.aggregate.assert_not_called()


@pytest.mark.unit
def test_lista_calcula_el_total_y_las_paginas(accesos_no_api, mocker):
    """
    TB-268: con 45 registros de 20 en 20 y offset 20, get_list_bitacora debe
    regresar el total, 3 páginas y la página actual 2, y pedirle a Mongo
    saltar 20 y traer 20. Si el cálculo falla, el paginador del front se
    salta registros o muestra páginas vacías.
    """
    cr = mongo_simulado(accesos_no_api, mocker, [[{"total": TOTAL_REGISTROS}], []])

    res = accesos_no_api.get_list_bitacora(LOCATION, AREA, limit=POR_PAGINA, offset=OFFSET_PAGINA_2)

    assert res["total_records"] == TOTAL_REGISTROS
    assert res["total_pages"] == PAGINAS_ESPERADAS
    assert res["actual_page"] == 2
    consulta = cr.aggregate.call_args_list[1].args[0]
    assert consulta[-2:] == [{"$skip": OFFSET_PAGINA_2}, {"$limit": POR_PAGINA}], f"Pidió {consulta[-2:]}"
