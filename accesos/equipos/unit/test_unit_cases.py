"""Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS.

./lkf test corre SOLO este archivo cuando cambia alguna funcion de
C10_TRIGGERS. Aqui van los casos principales de cada funcion y las
validaciones mas importantes; los demas unitarios de la seccion viven en
otros archivos de unit/ y se corren a mano.
"""

import pytest
from ..data.equipos_data import (
    EQUIPO_VISITA,
    EQUIPO_TIPO_CATALOGO,
    RENGLON_VACIO,
    EQUIPO_AGREGADO,
    TIPO_SINONIMO_CON_ACENTO,
    TIPO_FUERA_DEL_RADIO,
    NOMBRE_PROYECTOR,
    REGISTRO_BITACORA,
    EQUIPO_PASE_ETIQUETAS,
)

C10_TRIGGERS = [
    "_answers_equipos",
    "_answers_equipos_pase",
    "_tipo_equipo_bitacora",
    "catalogo_tipo_equipo",
    "format_equipos_simple",
    "update_bitacora_entrada",
]


# --- answers equipos ---
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


@pytest.mark.unit
def test_equipos_del_pase_guardan_el_tipo_en_el_catalogo_de_tipos(accesos_no_api):
    """
    TB-262: en el pase el tipo de equipo es un catálogo; _answers_equipos_pase
    debe mandarlo al catálogo de tipos de equipo tal como viene, y sin tipo no
    debe agregar el catálogo. Si manda el catálogo vacío, LinkaForm lo
    rechaza; si cambia el tipo, ya no coincide con el catálogo.
    """
    acc = accesos_no_api

    con_tipo, sin_tipo = acc._answers_equipos_pase([EQUIPO_VISITA, {**EQUIPO_VISITA, "tipo": ""}])

    assert con_tipo[acc.TIPO_DE_EQUIPO_OBJ_ID] == {acc.mf["tipo_equipo_pase"]: EQUIPO_VISITA["tipo"]}
    assert acc.TIPO_DE_EQUIPO_OBJ_ID not in sin_tipo, f"Sin tipo quedó {sin_tipo[acc.TIPO_DE_EQUIPO_OBJ_ID]!r}"
    assert con_tipo[acc.mf["numero_serie"]] == EQUIPO_VISITA["serie"]


# --- tipo equipo bitacora ---
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


# --- update bitacora entrada ---
@pytest.mark.unit
def test_agregar_equipo_a_una_entrada_lo_guarda_como_renglon_nuevo(accesos_no_api, mocker):
    """
    TB-316: con el equipo del modal de agregar equipo (add-local-equipo),
    update_bitacora_entrada debe agregarlo como renglón nuevo del grupo de
    equipos de la entrada, con tipo, nombre, marca, modelo, color y serie en
    sus campos. Si un dato cae fuera de su campo, la pestaña Equipos no lo
    muestra.
    """
    acc = accesos_no_api
    mf = acc.mf
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value={"status_code": 202})

    acc.update_bitacora_entrada({"equipo": dict(EQUIPO_AGREGADO)}, record_id=REGISTRO_BITACORA)

    guardar.assert_called_once()
    assert guardar.call_args.kwargs["record_id"] == [REGISTRO_BITACORA]
    renglones = guardar.call_args.kwargs["answers"][mf["grupo_equipos"]]
    assert list(renglones) == [-1], f"El equipo no se agregó como renglón nuevo: {list(renglones)}"
    equipo = renglones[-1]
    assert equipo[mf["tipo_equipo"]] == "herramienta", f"El tipo quedó {equipo[mf['tipo_equipo']]!r}"
    assert equipo[mf["nombre_articulo"]] == EQUIPO_AGREGADO["nombre"]
    assert equipo[mf["marca_articulo"]] == EQUIPO_AGREGADO["marca"]
    assert equipo[mf["modelo_articulo"]] == EQUIPO_AGREGADO["modelo"]
    assert equipo[mf["color_articulo"]] == EQUIPO_AGREGADO["color"]
    assert equipo[mf["numero_serie"]] == EQUIPO_AGREGADO["serie"]


# --- equipo del pase a la bitacora ---
@pytest.mark.unit
def test_equipo_del_pase_llega_completo_a_la_bitacora(accesos_no_api):
    """
    TB-319: al registrar la entrada, el equipo del pase (con las etiquetas
    del detalle del pase) pasa por format_equipos_simple y luego por
    _answers_equipos; debe llegar a la bitácora con el tipo del catálogo
    convertido a la opción del radio ('Laptop' a 'computo') y con nombre,
    marca, modelo, serie y color. Si se pierde uno, la pestaña Equipos
    muestra el equipo incompleto.
    """
    acc = accesos_no_api
    mf = acc.mf

    simple = acc.format_equipos_simple([dict(EQUIPO_PASE_ETIQUETAS)])
    equipo = acc._answers_equipos(simple)[0]

    assert equipo[mf["tipo_equipo"]] == "computo", f"El tipo quedó {equipo[mf['tipo_equipo']]!r}"
    assert equipo[mf["nombre_articulo"]] == EQUIPO_PASE_ETIQUETAS["nombre_articulo"]
    assert equipo[mf["marca_articulo"]] == EQUIPO_PASE_ETIQUETAS["marca_articulo"]
    assert equipo[mf["modelo_articulo"]] == EQUIPO_PASE_ETIQUETAS["modelo_articulo"]
    assert equipo[mf["numero_serie"]] == EQUIPO_PASE_ETIQUETAS["numero_serie"]
    assert equipo[mf["color_articulo"]] == EQUIPO_PASE_ETIQUETAS["color_articulo"]


# --- catalogo tipo equipo ---
@pytest.mark.unit
def test_catalogo_de_tipos_de_equipo_sale_del_catalogo_del_pase(accesos_no_api, mocker):
    """
    TB-320: el front pide el catálogo de tipos de equipo del pase
    (catalago_tipo_equipo); catalogo_tipo_equipo debe pedirlo al catálogo de
    tipos de equipo de la forma Pase de entrada. Si pide otro, el selector de
    tipo de equipo sale vacío o con otras opciones.
    """
    acc = accesos_no_api
    consultar = mocker.patch.object(acc.lkf_api, "catalog_view", return_value=[])

    acc.catalogo_tipo_equipo()

    consultar.assert_called_once()
    assert consultar.call_args.args[:2] == (acc.TIPO_EQUIPOS_CAT_ID, acc.PASE_ENTRADA)
