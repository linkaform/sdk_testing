# coding: utf-8

"""
Duración que guarda la salida (do_out) sin tocar preprod: se simulan la
visita abierta, el empleado y el guardado, y se revisa lo que do_out manda
a guardar.
Notion: TB-063.
"""

from datetime import datetime

import pytest
import pytz

from ..data.bitacora_data import (
    LOCATION,
    AREA,
    VISITA_ABIERTA_DURACION,
    MARGEN_HORA_SALIDA,
    ZONA_EMPLEADO_OTRA,
    ENTRADA_HACE_10_MIN,
    DURACION_10_MIN,
)


@pytest.mark.unit
def test_do_out_usa_la_zona_horaria_del_empleado(accesos_no_api, mocker):
    """
    TB-063: la entrada se guarda con la zona del empleado; la salida también
    debe usarla. Con un empleado en Cancún y una entrada de hace 10 min, la
    salida debe quedar en hora de Cancún y durar 10 min (hoy se guarda en
    hora de CDMX y la duración sale casi de un día).
    """
    ahora_empleado = datetime.now(pytz.timezone(ZONA_EMPLEADO_OTRA)).replace(tzinfo=None)
    entrada = (ahora_empleado - ENTRADA_HACE_10_MIN).strftime("%Y-%m-%d %H:%M:%S")

    accesos_no_api.user["timezone"] = ZONA_EMPLEADO_OTRA
    mocker.patch.object(accesos_no_api, "get_employee_data", return_value={"timezone": ZONA_EMPLEADO_OTRA})
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
