# coding: utf-8

"""
Salida masiva (force_quit_all_persons) sin tocar preprod: se simulan la
consulta a Mongo y el guardado, porque la función real cierra visitas de
toda la cuenta.
Notion: TB-072 y TB-077.
"""

from datetime import datetime

import pytest
import pytz

from ..data.bitacora_data import (
    LOCATION,
    VISITAS_ABIERTAS_OTRAS_UBICACIONES,
    VISITAS_ABIERTAS_UBICACION,
    DURACION_CIERRE_GENERAL,
    ZONA_EMPLEADO_OTRA,
    MARGEN_HORA_SALIDA,
)


@pytest.mark.unit
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
def test_force_quit_guarda_cierre_general_y_hora_del_empleado(accesos_no_api, mocker):
    """
    TB-077: el cierre general de una ubicación guarda la salida en la hora
    del empleado y "Cierre general" como duración, porque no se sabe a qué
    hora salió cada persona (hoy usa hora de CDMX y no llena la duración).
    """
    ahora_empleado = datetime.now(pytz.timezone(ZONA_EMPLEADO_OTRA)).replace(tzinfo=None)

    accesos_no_api.user["timezone"] = ZONA_EMPLEADO_OTRA
    mocker.patch.object(accesos_no_api, "get_employee_data", return_value={"timezone": ZONA_EMPLEADO_OTRA})
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
