"""Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS.

./lkf test corre SOLO este archivo cuando cambia alguna funcion de
C10_TRIGGERS. Aqui van los casos principales de cada funcion y las
validaciones mas importantes; los demas unitarios de la seccion viven en
otros archivos de unit/ y se corren a mano.
"""

import pytest
import pytz
from ..data.bitacora_data import (
    LOCATION,
    AREA,
    OTRA_LOCATION,
    FILTRO_ENTRADAS,
    FILTRO_SALIDAS,
    FILTRO_RANGO,
    DIA_CONSULTA,
    FIN_DIA_CONSULTA,
    PERFIL_PANEL,
    VISITA_A_PANEL,
    FILTROS_PANEL,
    FILTRO_DESCONOCIDO,
    VISITA_ABIERTA_DURACION,
    MARGEN_HORA_SALIDA,
    ZONA_EMPLEADO_OTRA,
    ENTRADA_HACE_10_MIN,
    DURACION_10_MIN,
    ZONA_EMPLEADO_CDMX,
    ENTRADA_HACE_MAS_DE_UN_DIA,
    DURACION_MAS_DE_UN_DIA,
    GAFETE_SIN_DEVOLVER,
    OTRA_UBICACION_ENTRADA,
    VISITAS_ABIERTAS_OTRAS_UBICACIONES,
    VISITAS_ABIERTAS_UBICACION,
    DURACION_CIERRE_GENERAL,
    POR_PAGINA,
    TOTAL_REGISTROS,
    OFFSET_PAGINA_2,
    PAGINAS_ESPERADAS,
)
from datetime import datetime
from lkf_back import de

C10_TRIGGERS = [
    "bitacora_base_match",
    "do_out",
    "force_quit_all_persons",
    "get_list_bitacora",
]


def mongo_simulado(acceso_obj, mocker, respuestas):
    """Reemplaza la conexión a Mongo; cada llamada a aggregate regresa la siguiente respuesta."""
    cr = mocker.MagicMock()
    cr.aggregate.side_effect = respuestas
    mocker.patch.object(acceso_obj, "cr", cr, create=True)
    return cr


# --- bitacora base match ---
@pytest.mark.unit
def test_filtro_usa_la_ubicacion_en_texto_o_en_lista_y_la_caseta(accesos_no_api):
    """
    TB-264: una ubicación en texto debe filtrar exacto y una lista de
    ubicaciones con $in; la caseta entra al filtro. Siempre se filtra la
    forma de bitácora sin los registros borrados. Si no, la lista mezcla
    visitas de otras plantas o casetas.
    """
    acc = accesos_no_api
    ubicacion = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID}.{acc.mf['ubicacion']}"
    caseta = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID}.{acc.mf['nombre_area']}"

    filtro = acc.bitacora_base_match(LOCATION, AREA)
    assert filtro["form_id"] == acc.BITACORA_ACCESOS
    assert filtro["deleted_at"] == {"$exists": False}
    assert filtro[ubicacion] == LOCATION
    assert filtro[caseta] == AREA

    varias = acc.bitacora_base_match([LOCATION, OTRA_LOCATION])
    assert varias[ubicacion] == {"$in": [LOCATION, OTRA_LOCATION]}, f"Filtró {varias[ubicacion]!r}"


@pytest.mark.unit
def test_en_salidas_la_fecha_que_se_filtra_es_la_de_salida(accesos_no_api):
    """
    TB-265: en Salidas (estatus 'salida') el rango de fechas debe aplicarse a
    la fecha de salida; en Entradas, a la de entrada. Si Salidas filtra por
    la entrada, quien entró ayer y salió hoy no aparece en las salidas de hoy.
    """
    acc = accesos_no_api
    fecha_salida = f"answers.{acc.mf['fecha_salida']}"
    fecha_entrada = f"answers.{acc.mf['fecha_entrada']}"
    rango = {"$gte": DIA_CONSULTA, "$lte": FIN_DIA_CONSULTA}

    salidas = acc.bitacora_base_match(
        LOCATION, AREA, dateFrom=DIA_CONSULTA, dateTo=DIA_CONSULTA, filterDate=FILTRO_RANGO, dynamic_filters=FILTRO_SALIDAS
    )
    assert salidas.get(fecha_salida) == rango, f"Salidas filtró la fecha de salida con {salidas.get(fecha_salida)!r}"
    assert fecha_entrada not in salidas, "Salidas filtró por la fecha de entrada"

    entradas = acc.bitacora_base_match(
        LOCATION, AREA, dateFrom=DIA_CONSULTA, dateTo=DIA_CONSULTA, filterDate=FILTRO_RANGO, dynamic_filters=FILTRO_ENTRADAS
    )
    assert entradas.get(fecha_entrada) == rango, f"Entradas filtró la fecha de entrada con {entradas.get(fecha_entrada)!r}"


# --- do out duracion ---
@pytest.mark.unit
@pytest.mark.target("do_out")
@pytest.mark.bug(1477)
def test_do_out_usa_la_zona_horaria_del_empleado(accesos_no_api, mocker):
    """
    TB-063: la entrada se guarda con la zona del empleado; la salida también
    debe usarla. Con un empleado en Cancún y una entrada de hace 10 min, la
    salida debe quedar en hora de Cancún y durar 10 min (antes se guardaba
    en hora de CDMX y la duración salía casi de un día).
    Bug 2610-1477 corregido (addons e8a511d).
    """
    ahora_empleado = datetime.now(pytz.timezone(ZONA_EMPLEADO_OTRA)).replace(tzinfo=None)
    entrada = (ahora_empleado - ENTRADA_HACE_10_MIN).strftime("%Y-%m-%d %H:%M:%S")

    accesos_no_api.user["timezone"] = ZONA_EMPLEADO_OTRA
    mocker.patch.object(de(accesos_no_api, "get_employee_data"), "get_employee_data", return_value={"timezone": ZONA_EMPLEADO_OTRA})
    mocker.patch.object(
        accesos_no_api, "get_last_user_move", return_value={**VISITA_ABIERTA_DURACION, "checkin_date": entrada}
    )
    mocker.patch.object(accesos_no_api, "get_booth_locations", return_value=[LOCATION])
    mocker.patch.object(accesos_no_api, "user_in_facility", return_value=True)
    guardar = mocker.patch.object(
        accesos_no_api.lkf_api, "patch_multi_record", return_value={"status_code": 202, "json": {}}
    )

    accesos_no_api.do_out(VISITA_ABIERTA_DURACION["folio"], LOCATION, AREA)

    answers = guardar.call_args.kwargs["answers"]
    salida = datetime.strptime(answers[accesos_no_api.mf["fecha_salida"]], "%Y-%m-%d %H:%M:%S")
    assert abs(salida - ahora_empleado) < MARGEN_HORA_SALIDA, (
        f"La salida se guardó a las {salida:%H:%M} y la hora del empleado es {ahora_empleado:%H:%M}"
    )
    duracion = answers[accesos_no_api.mf["duracion"]]
    assert duracion == DURACION_10_MIN, f"Una visita de 10 min quedó con duración '{duracion}'"


# --- do out validaciones ---
@pytest.mark.unit
def test_no_se_registra_la_salida_si_no_se_ha_devuelto_el_gafete(accesos_no_api, mocker):
    """
    TB-185: si la visita tiene el gafete asignado y no se ha devuelto,
    do_out debe detenerse con el aviso de liberar el gafete y no guardar la
    salida. Si la guarda, la persona sale con el gafete y queda 'En Uso'.
    """
    visita = {**VISITA_ABIERTA_DURACION, "status_gafete": GAFETE_SIN_DEVOLVER}
    mocker.patch.object(accesos_no_api, "get_last_user_move", return_value=visita)
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "patch_multi_record")

    with pytest.raises(Exception, match="liberar el gafete"):
        accesos_no_api.do_out(VISITA_ABIERTA_DURACION["folio"], LOCATION, AREA)
    guardar.assert_not_called()


@pytest.mark.unit
def test_no_se_puede_salir_por_otra_ubicacion_distinta_a_la_de_entrada(accesos_no_api, mocker):
    """
    TB-186: si la persona entró por otra ubicación, do_out en una caseta de
    esta ubicación debe detenerse con el aviso de dónde ingresó y no guardar
    la salida. Si la guarda, la bitácora registra una salida por un lugar
    por el que la persona no entró.
    """
    visita = {**VISITA_ABIERTA_DURACION, "ubicacion_entrada": OTRA_UBICACION_ENTRADA}
    mocker.patch.object(accesos_no_api, "get_last_user_move", return_value=visita)
    mocker.patch.object(accesos_no_api, "get_booth_locations", return_value=[LOCATION])
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "patch_multi_record")

    with pytest.raises(Exception, match="no puede salir en"):
        accesos_no_api.do_out(VISITA_ABIERTA_DURACION["folio"], LOCATION, AREA)
    guardar.assert_not_called()


@pytest.mark.unit
def test_sin_entrada_registrada_la_salida_responde_un_error_claro(accesos_no_api, mocker):
    """
    TB-187: si el pase no tiene una entrada registrada en la ubicación,
    do_out debe detenerse con el aviso de que no hay entrada y no guardar
    nada. Si truena con otro error, el guardia no sabe por qué no puede
    registrar la salida.
    """
    mocker.patch.object(accesos_no_api, "get_last_user_move", return_value={})
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "patch_multi_record")

    with pytest.raises(Exception, match="no tiene una entrada registrada"):
        accesos_no_api.do_out(VISITA_ABIERTA_DURACION["folio"], LOCATION, AREA)
    guardar.assert_not_called()


# --- force quit all persons ---
@pytest.mark.unit
@pytest.mark.target("force_quit_all_persons")
def test_force_quit_sin_ubicacion_no_cierra_otras_ubicaciones(accesos_no_api, mocker):
    """
    TB-072: sin ubicación (location vacío), la salida masiva no debe cerrar las visitas
    abiertas de otras ubicaciones de la cuenta. Puede rechazar la llamada,
    pero no guardar la salida de esas visitas.
    """
    mocker.patch.object(accesos_no_api.cr, "aggregate", return_value=VISITAS_ABIERTAS_OTRAS_UBICACIONES)
    guardar = mocker.patch.object(
        accesos_no_api.lkf_api, "patch_multi_record", return_value={"status_code": 202, "json": {}}
    )

    try:
        accesos_no_api.force_quit_all_persons(location="")
    except Exception:
        pass

    assert not guardar.called, (
        f"Sin ubicación registró la salida de {len(guardar.call_args.kwargs['record_id'])} visitas de toda la cuenta"
    )


@pytest.mark.unit
@pytest.mark.target("force_quit_all_persons")
@pytest.mark.bug(1477)
def test_force_quit_guarda_cierre_general_y_hora_del_empleado(accesos_no_api, mocker):
    """
    TB-077: el cierre general de una ubicación guarda la salida en la hora
    del empleado y "Cierre general" como duración, porque no se sabe a qué
    hora salió cada persona (antes usaba hora de CDMX y no llenaba la duración).
    Bug 2610-1477 corregido (addons e8a511d).
    """
    ahora_empleado = datetime.now(pytz.timezone(ZONA_EMPLEADO_OTRA)).replace(tzinfo=None)

    accesos_no_api.user["timezone"] = ZONA_EMPLEADO_OTRA
    mocker.patch.object(de(accesos_no_api, "get_employee_data"), "get_employee_data", return_value={"timezone": ZONA_EMPLEADO_OTRA})
    mocker.patch.object(accesos_no_api.cr, "aggregate", return_value=VISITAS_ABIERTAS_UBICACION)
    guardar = mocker.patch.object(
        accesos_no_api.lkf_api, "patch_multi_record", return_value={"status_code": 202, "json": {}}
    )

    accesos_no_api.force_quit_all_persons(location=LOCATION)

    answers = guardar.call_args.kwargs["answers"]
    salida = datetime.strptime(answers[accesos_no_api.mf["fecha_salida"]], "%Y-%m-%d %H:%M:%S")
    assert abs(salida - ahora_empleado) < MARGEN_HORA_SALIDA, (
        f"La salida se guardó a las {salida:%H:%M} y la hora del empleado es {ahora_empleado:%H:%M}"
    )
    duracion = answers.get(accesos_no_api.mf["duracion"])
    assert duracion == DURACION_CIERRE_GENERAL, f"El cierre general quedó con duración '{duracion}'"


# --- list bitacora paginacion ---
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
