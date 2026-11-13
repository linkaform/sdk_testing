# coding: utf-8

"""
Crear un rondín (create_recorrido_rondin) con su asignación, a quién se le
asigna (rondin_asignado_a) y pausar/reanudar (pause_or_play_rondin), sin tocar
la cuenta: se simulan la ubicación, las áreas, el empleado y el guardado.
Notion: TB-294 a TB-298 (pendientes de dar de alta).
"""

import pytest

from ..data.rondines_data import (
    RONDIN_NUEVO,
    GRUPO_RONDIN,
    ROLES_RONDIN,
    PERSONA_RONDIN,
    RONDIN_ID,
    PATCH_OK,
    PATCH_ERROR,
)

pytestmark = pytest.mark.back("sanic")


def crear_simulado(acc, mocker):
    mocker.patch.object(acc, "get_ubicacion_geolocation", return_value=None)
    mocker.patch.object(acc, "get_areas_details", return_value=None)
    return mocker.patch.object(acc, "create_register", return_value={"status_code": 201})


@pytest.mark.unit
@pytest.mark.target("create_recorrido_rondin")
def test_rondin_asignado_a_un_grupo_guarda_el_grupo_y_no_una_persona(accesos_no_api, mocker):
    """
    TB-294: un rondín asignado a un grupo guarda el grupo en su catálogo y no
    llena "Asignado a": queda sin usuario hasta que un guardia del grupo lo
    inicia (si se asigna a una persona, al resto no le aparece).
    """
    acc = accesos_no_api
    guardar = crear_simulado(acc, mocker)
    asignar = mocker.patch.object(acc, "rondin_asignado_a")

    acc.create_recorrido_rondin({**RONDIN_NUEVO, "tipo_asignacion": "grupo", "asignado_a": [GRUPO_RONDIN]})

    answers = guardar.call_args.kwargs["answers"]
    assert answers[acc.GRUPOS_CAT_OBJ_ID] == {acc.rondin_keys["grupo_asignado"]: GRUPO_RONDIN}
    assert answers[acc.rondin_keys["tipo_asignacion"]] == "grupo"
    assert acc.rondin_keys["grupo_asignado_a"] not in answers
    assert not asignar.called


@pytest.mark.unit
@pytest.mark.target("create_recorrido_rondin")
def test_rondin_por_rol_guarda_cada_rol_en_su_renglon(accesos_no_api, mocker):
    """
    TB-295: con roles, el rondín guarda un renglón por rol con el rol en su
    catálogo. Es lo que usa la bandeja para mostrarlo a los guardias de esos roles.
    """
    acc = accesos_no_api
    guardar = crear_simulado(acc, mocker)

    acc.create_recorrido_rondin({**RONDIN_NUEVO, "tipo_asignacion": "rol", "roles": list(ROLES_RONDIN)})

    renglones = guardar.call_args.kwargs["answers"][acc.f["grupo_roles"]]
    assert [r[acc.ROL_CATALOG_OBJ_ID][acc.f["rol"]] for r in renglones] == ROLES_RONDIN


@pytest.mark.unit
@pytest.mark.target("create_recorrido_rondin", "rondin_asignado_a")
def test_rondin_para_una_persona_la_guarda_en_asignado_a(accesos_no_api, mocker):
    """
    TB-296: asignado a una persona específica, el rondín guarda a esa persona
    (como la arma rondin_asignado_a) en "Asignado a".
    """
    acc = accesos_no_api
    guardar = crear_simulado(acc, mocker)
    persona = [{"empleado": PERSONA_RONDIN}]
    asignar = mocker.patch.object(acc, "rondin_asignado_a", return_value=persona)

    acc.create_recorrido_rondin({**RONDIN_NUEVO, "tipo_asignacion": "persona_especifica", "asignado_a": [PERSONA_RONDIN]})

    asignar.assert_called_once_with(PERSONA_RONDIN)
    assert guardar.call_args.kwargs["answers"][acc.rondin_keys["grupo_asignado_a"]] == persona


@pytest.mark.unit
@pytest.mark.target("rondin_asignado_a")
def test_persona_que_no_esta_en_empleados_se_asigna_por_nombre(accesos_no_api, mocker):
    """
    TB-297: si la persona no aparece en el catálogo de empleados, el rondín
    no se queda sin asignar: se guarda su nombre en el catálogo de empleados.
    """
    acc = accesos_no_api
    mocker.patch.object(acc.Employee, "get_employee_data", return_value={})
    mocker.patch.object(acc, "visita_a_set_format", return_value={})

    asignados = acc.rondin_asignado_a(PERSONA_RONDIN)

    assert asignados == [{acc.Employee.CONF_AREA_EMPLEADOS_CAT_OBJ_ID: {acc.mf["nombre_empleado"]: PERSONA_RONDIN}}]


@pytest.mark.unit
@pytest.mark.target("pause_or_play_rondin")
def test_pausar_y_reanudar_cambian_la_accion_de_la_recurrencia(accesos_no_api, mocker):
    """
    TB-298: pausar guarda la acción 'pausar' y reanudar 'programar' sobre el
    rondín; si LinkaForm lo rechaza, se responde error (no "pausado con éxito").
    """
    acc = accesos_no_api
    accion = acc.rondin_keys["accion_recurrencia"]
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value=dict(PATCH_OK))

    acc.pause_or_play_rondin(RONDIN_ID, paused=True)
    assert guardar.call_args.kwargs["answers"] == {accion: "pausar"}
    assert guardar.call_args.kwargs["record_id"] == [RONDIN_ID]

    acc.pause_or_play_rondin(RONDIN_ID, paused=False)
    assert guardar.call_args.kwargs["answers"] == {accion: "programar"}

    guardar.return_value = dict(PATCH_ERROR)
    assert acc.pause_or_play_rondin(RONDIN_ID, paused=True)["status_code"] == 400
