"""Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS.

./lkf test corre SOLO este archivo cuando cambia alguna funcion de
C10_TRIGGERS. Aqui van los casos principales de cada funcion y las
validaciones mas importantes; los demas unitarios de la seccion viven en
otros archivos de unit/ y se corren a mano.
"""

import pytest
from lkf_back import de
from ..data.vehiculos_data import (
    VEHICULO_VISITA,
    VEHICULO_LLAVES_LARGAS,
    RENGLON_VACIO,
    LOCATION,
    AREA,
    DESGLOSE_VEHICULOS,
    FILTRO_DENTRO,
    LIMITE_LISTA,
)

C10_TRIGGERS = [
    "_answers_vehiculos",
    "_answers_vehiculos_pase",
    "_size_vehiculos_con_tipo",
    "format_vehiculos_simple",
    "get_list_bitacora",
]


# --- answers vehiculos ---
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


# --- lista vehiculos ---
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
    tipo = f"answers.{grupo}.{de(acc, "TIPO_DE_VEHICULO_OBJ_ID").TIPO_DE_VEHICULO_OBJ_ID}.{acc.mf['tipo_vehiculo']}"
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
    tipo = f"$$v.{de(acc, "TIPO_DE_VEHICULO_OBJ_ID").TIPO_DE_VEHICULO_OBJ_ID}.{acc.mf['tipo_vehiculo']}"

    expresion = acc._size_vehiculos_con_tipo("$vehiculos")

    filtro = expresion["$size"]["$filter"]
    assert filtro["input"] == "$vehiculos"
    assert filtro["as"] == "v"
    assert filtro["cond"] == {"$not": [{"$in": [{"$ifNull": [tipo, None]}, ["", None]]}]}, (
        f"La condición del contador es {filtro['cond']}"
    )
