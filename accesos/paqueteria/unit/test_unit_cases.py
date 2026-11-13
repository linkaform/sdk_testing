"""Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS.

./lkf test corre SOLO este archivo cuando cambia alguna funcion de
C10_TRIGGERS. Aqui van los casos principales de cada funcion y las
validaciones mas importantes; los demas unitarios de la seccion viven en
otros archivos de unit/ y se corren a mano.
"""

import copy
import pytest
from ..data.paqueteria_data import (
    LOCATION,
    AREA,
    PAQUETE_UNIT,
    PAQUETE_UNIT_OTRO,
    DESTINATARIO_EXTERNO,
    METADATA_PAQUETE,
    GUARDADO_OK,
    GUARDADO_FALLIDO,
    CANALES_CORREO,
    AVISO_CORREO,
    AVISO_ENVIADO,
    AVISO_SIN_EMAIL,
    OTRA_UBICACION,
    ESTATUS_GUARDADO,
    ESTATUS_TODOS,
)

C10_TRIGGERS = [
    "create_paquete",
    "paqueteria_base_match",
]


def guardar_paquete(acceso_obj, mocker, paquete, respuesta=GUARDADO_OK, notificacion=None):
    """Crea el paquete con el guardado simulado; regresa (respuesta, mock del guardado)."""
    mocker.patch.object(acceso_obj.lkf_api, "get_metadata", return_value=dict(METADATA_PAQUETE))
    guardar = mocker.patch.object(acceso_obj.lkf_api, "post_forms_answers", return_value=dict(respuesta))
    res = acceso_obj.create_paquete(copy.deepcopy(paquete), notificacion=notificacion)
    return res, guardar


# --- create paquete ---
@pytest.mark.unit
def test_recibir_paquete_guarda_ubicacion_caseta_y_locker_en_sus_catalogos(accesos_no_api, mocker):
    """
    TB-246: create_paquete debe guardar la ubicación en el catálogo de
    ubicaciones, la caseta en el de áreas y el locker en el de lockers. Si
    se pierde uno, el paquete no aparece al filtrar por su caseta o nadie
    sabe en qué locker quedó.
    """
    acc = accesos_no_api

    _, guardar = guardar_paquete(acc, mocker, PAQUETE_UNIT)

    answers = guardar.call_args.args[0]["answers"]
    assert answers[acc.UBICACIONES_CAT_OBJ_ID] == {acc.mf["ubicacion"]: LOCATION}
    assert answers[acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID] == {acc.mf["nombre_area"]: AREA}
    assert answers[acc.LOCKERS_CAT_OBJ_ID] == {acc.mf["locker_id"]: PAQUETE_UNIT["guardado_en_paqueteria"]}


@pytest.mark.unit
def test_destinatario_se_guarda_como_empleado_o_como_otro(accesos_no_api, mocker):
    """
    TB-247: un destinatario empleado debe guardarse en el catálogo de
    empleados; uno externo ("Otro") en el campo de texto quien_recibe_otro.
    Si se cruzan, el aviso y la entrega no encuentran a quién va el paquete.
    """
    acc = accesos_no_api

    _, guardar = guardar_paquete(acc, mocker, PAQUETE_UNIT)
    answers = guardar.call_args.args[0]["answers"]
    assert answers[acc.CONF_AREA_EMPLEADOS_CAT_OBJ_ID] == {
        acc.mf["nombre_empleado"]: PAQUETE_UNIT["quien_recibe_paqueteria"],
    }

    _, guardar = guardar_paquete(acc, mocker, PAQUETE_UNIT_OTRO)
    answers = guardar.call_args.args[0]["answers"]
    assert answers[acc.paquetes_fields["quien_recibe_otro"]] == DESTINATARIO_EXTERNO
    assert acc.CONF_AREA_EMPLEADOS_CAT_OBJ_ID not in answers, "El destinatario externo quedó en el catálogo de empleados"


@pytest.mark.unit
def test_aviso_solo_se_manda_si_el_paquete_se_guardo(accesos_no_api, mocker):
    """
    TB-248: create_paquete debe avisar al destinatario solo si el paquete se
    guardó; si el guardado falla, no avisa. La llave anterior
    notificacion_paqueteria no es campo de la forma: no se guarda y se usa
    como canales del aviso. Si se avisa sin guardar, el destinatario va por
    un paquete que no está registrado.
    """
    acc = accesos_no_api
    avisar = mocker.patch.object(acc, "_notificar_paquete_recibido", return_value=dict(AVISO_ENVIADO))

    res, _ = guardar_paquete(acc, mocker, PAQUETE_UNIT, notificacion=AVISO_CORREO)
    avisar.assert_called_once()
    assert res["notificaciones"] == AVISO_ENVIADO

    avisar.reset_mock()
    guardar_paquete(acc, mocker, PAQUETE_UNIT, respuesta=GUARDADO_FALLIDO, notificacion=AVISO_CORREO)
    avisar.assert_not_called()

    avisar.reset_mock()
    _, guardar = guardar_paquete(acc, mocker, {**PAQUETE_UNIT, "notificacion_paqueteria": CANALES_CORREO})
    avisar.assert_called_once()
    assert avisar.call_args.args[1] == {"canales": CANALES_CORREO}
    assert "notificacion_paqueteria" not in guardar.call_args.args[0]["answers"]


# --- notificar paquete ---
@pytest.mark.unit
def test_aviso_por_correo_sin_email_reporta_el_error_y_no_se_envia(accesos_no_api, mocker):
    """
    TB-249: con el canal correo y sin email del destinatario, el aviso debe
    reportar "Sin email del destinatario" para el correo y no intentar
    enviarlo. Si intenta enviarlo, truena o el guardia cree que se avisó.
    """
    enviar = mocker.patch.object(accesos_no_api, "send_email_notification")

    resultado = accesos_no_api._notificar_paquete_recibido(dict(PAQUETE_UNIT), dict(AVISO_SIN_EMAIL))

    assert resultado["correo"] == {"ok": False, "error": "Sin email del destinatario"}
    enviar.assert_not_called()


# --- paqueteria base match ---
@pytest.mark.unit
def test_filtro_usa_la_ubicacion_la_caseta_y_el_estatus_de_la_pestana(accesos_no_api):
    """
    TB-245: una ubicación en texto debe filtrar exacto y la lista de
    ubicaciones del header con $in, ganando sobre la de texto. Pendientes
    manda el estatus 'guardado' y la caseta; los dos deben entrar al filtro.
    Todos no filtra por estatus. Si no, la lista mezcla paquetes de otras
    casetas o ya entregados.
    """
    acc = accesos_no_api
    campos = acc.paquetes_fields
    ubicacion = f"answers.{campos['ubicacion_paqueteria']}"
    caseta = f"answers.{campos['area_paqueteria']}"
    estatus = f"answers.{campos['estatus_paqueteria']}"

    filtro = acc.paqueteria_base_match(location=LOCATION, area=AREA, status=ESTATUS_GUARDADO)
    assert filtro["form_id"] == acc.PAQUETERIA
    assert filtro["deleted_at"] == {"$exists": False}
    assert filtro[ubicacion] == LOCATION
    assert filtro[caseta] == AREA
    assert filtro[estatus] == ESTATUS_GUARDADO

    varias = acc.paqueteria_base_match(location=LOCATION, locations=[LOCATION, OTRA_UBICACION])
    assert varias[ubicacion] == {"$in": [LOCATION, OTRA_UBICACION]}, f"Filtró {varias[ubicacion]!r}"

    todos = acc.paqueteria_base_match(location=LOCATION, status=ESTATUS_TODOS)
    assert estatus not in todos, f"Todos filtró por estatus {todos[estatus]!r}"
