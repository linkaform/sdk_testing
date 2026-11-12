# coding: utf-8

"""
Pestaña Vehículos de Bitácoras y su contador: get_list_bitacora con
desglose='vehiculos' y la regla del contador de vehículos dentro
(_size_vehiculos_con_tipo). Se simula la consulta a Mongo y se revisa el
filtro que se arma.
Notion: TB-257 y TB-258.
"""

import pytest

from ..data.vehiculos_data import LOCATION, AREA, DESGLOSE_VEHICULOS, FILTRO_DENTRO, LIMITE_LISTA


@pytest.mark.unit
def test_pestana_vehiculos_muestra_una_fila_por_vehiculo_sin_los_que_no_tienen_tipo(accesos_no_api, mocker):
    """
    TB-257: con desglose='vehiculos', get_list_bitacora debe pedir solo
    bitácoras con vehículos, desglosar el grupo (una fila por vehículo) y
    omitir los que no tienen tipo, igual en el total que en la lista. Si el
    total cuenta otra cosa, la paginación muestra páginas vacías.
    """
    acc = accesos_no_api
    grupo = acc.mf["grupo_vehiculos"]
    tipo = f"answers.{grupo}.{acc.TIPO_DE_VEHICULO_OBJ_ID}.{acc.mf['tipo_vehiculo']}"
    cr = mocker.MagicMock()
    cr.aggregate.return_value = []
    mocker.patch.object(acc, "cr", cr, create=True)

    acc.get_list_bitacora(
        location=LOCATION, area=AREA, dynamic_filters=FILTRO_DENTRO, limit=LIMITE_LISTA, desglose=DESGLOSE_VEHICULOS
    )

    conteo, lista = (c.args[0] for c in cr.aggregate.call_args_list)
    for consulta in (conteo, lista):
        assert consulta[0]["$match"][f"answers.{grupo}.0"] == {"$exists": True}
        assert consulta[1]["$unwind"]["path"] == f"$answers.{grupo}"
        assert consulta[2] == {"$match": {tipo: {"$nin": ["", None]}}}, f"Filtro de tipo: {consulta[2]}"


@pytest.mark.unit
def test_contador_de_vehiculos_dentro_no_cuenta_los_que_no_tienen_tipo(accesos_no_api):
    """
    TB-258: el contador de vehículos dentro cuenta con
    _size_vehiculos_con_tipo; debe contar solo los vehículos con tipo
    (descarta tipo vacío o nulo), la misma regla que la lista. Si cuenta los
    renglones vacíos, la tarjeta marca más vehículos de los que hay en la
    lista (ticket 2610-1484).
    """
    acc = accesos_no_api
    tipo = f"$$v.{acc.TIPO_DE_VEHICULO_OBJ_ID}.{acc.mf['tipo_vehiculo']}"

    expresion = acc._size_vehiculos_con_tipo("$vehiculos")

    filtro = expresion["$size"]["$filter"]
    assert filtro["input"] == "$vehiculos"
    assert filtro["as"] == "v"
    assert filtro["cond"] == {"$not": [{"$in": [{"$ifNull": [tipo, None]}, ["", None]]}]}, (
        f"La condición del contador es {filtro['cond']}"
    )
