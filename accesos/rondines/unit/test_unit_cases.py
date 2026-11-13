# coding: utf-8

"""Rondines: reclamar (claim_rondin, claim_group_rondin), crear con su
asignacion (create_recorrido_rondin, rondin_asignado_a) y pausar/reanudar
(pause_or_play_rondin), sin tocar la cuenta.
Notion: TB-289 a TB-298.

Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS:
./lkf test corre este archivo cuando cambia alguna funcion de C10_TRIGGERS.
La seccion la sirve Sanic en prod: los tests llevan back("sanic") y en addons
salen SKIPPED.
"""

from bson import ObjectId
from types import SimpleNamespace

import pytest

from ..data.rondines_data import (
    USER_ID_GUARDIA,
    USUARIO_GUARDIA,
    RONDIN_ID,
    HERMANO_ID,
    PADRE_ID,
    PATCH_OK,
    PATCH_ERROR,
    RONDIN_NUEVO,
    GRUPO_RONDIN,
    ROLES_RONDIN,
    PERSONA_RONDIN,
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["claim_group_rondin", "claim_rondin", "create_recorrido_rondin", "pause_or_play_rondin", "rondin_asignado_a"]


def rondin_de_grupo(acc):
    """Registro de la bitácora asignado a un grupo, sin padre y sin usuario."""
    return {"_id": ObjectId(RONDIN_ID), "answers": {acc.rondin_keys["tipo_asignacion"]: "grupo"}}


def reclamo_simulado(acc, mocker, bloqueados=1, guardado=PATCH_OK):
    """Mongo regresa `bloqueados` en el update_one del bloqueo (0 = ya lo tomó otro)."""
    cr = mocker.MagicMock()
    cr.update_one.return_value = SimpleNamespace(matched_count=bloqueados)
    mocker.patch.object(acc, "cr", cr)
    mocker.patch.object(acc.lkf_api, "get_user_by_id", return_value=dict(USUARIO_GUARDIA))
    return {
        "cr": cr,
        "guardar": mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value=dict(guardado)),
        "inbox": mocker.patch.object(acc, "remove_group_inbox", return_value=2),
        "split": mocker.patch.object(acc, "split_group_rondin", return_value=(True, {"split": True})),
    }


@pytest.mark.unit
@pytest.mark.target("claim_group_rondin")
def test_quien_inicia_un_rondin_de_grupo_se_lo_queda_y_sale_del_inbox_de_los_demas(accesos_no_api, mocker):
    """
    TB-289: el guardia que inicia un rondín de grupo queda en "Asignado a",
    el rondín pasa a 'en_proceso' y se quita del inbox de los demás guardias
    del grupo (pero no del suyo). El bloqueo solo toma el rondín si sigue
    'programado' y sin usuario.
    """
    acc = accesos_no_api
    mocks = reclamo_simulado(acc, mocker)

    ok, data = acc.claim_group_rondin(rondin_de_grupo(acc), user_id=USER_ID_GUARDIA)

    assert ok, data
    filtro, cambio = mocks["cr"].update_one.call_args_list[0].args
    assert filtro[f"answers.{acc.f['estatus_del_recorrido']}"] == "programado"
    assert f"answers.{acc.USUARIOS_OBJ_ID}.{acc.mf['id_usuario']}" in filtro, "El bloqueo no revisa que no tenga usuario"
    answers = mocks["guardar"].call_args.kwargs["answers"]
    assert answers[acc.USUARIOS_OBJ_ID][acc.mf["id_usuario"]] == [USER_ID_GUARDIA]
    assert answers[acc.f["estatus_del_recorrido"]] == "en_proceso"
    assert mocks["inbox"].call_args.kwargs["keep_user_id"] == USER_ID_GUARDIA


@pytest.mark.unit
@pytest.mark.target("claim_group_rondin")
def test_si_otro_guardia_ya_lo_inicio_su_trabajo_se_guarda_aparte(accesos_no_api, mocker):
    """
    TB-290: si otro guardia ganó el rondín (el bloqueo no encuentra el
    registro 'programado'), no se le quita: el recorrido de este guardia va a
    una bitácora aparte (split_group_rondin) y no se toca el registro ganado.
    """
    acc = accesos_no_api
    mocks = reclamo_simulado(acc, mocker, bloqueados=0)

    acc.claim_group_rondin(rondin_de_grupo(acc), user_id=USER_ID_GUARDIA)

    mocks["split"].assert_called_once()
    assert not mocks["guardar"].called, "Reasignó un rondín que ya había tomado otro guardia"
    assert not mocks["inbox"].called


@pytest.mark.unit
@pytest.mark.target("claim_group_rondin")
def test_si_no_se_puede_guardar_el_reclamo_el_rondin_vuelve_a_programado(accesos_no_api, mocker):
    """
    TB-291: si LinkaForm rechaza la asignación, el rondín debe regresar a
    'programado' (si se queda 'reclamado', nadie más lo puede iniciar) y
    seguir en el inbox de todos.
    """
    acc = accesos_no_api
    mocks = reclamo_simulado(acc, mocker, guardado=PATCH_ERROR)

    ok, _ = acc.claim_group_rondin(rondin_de_grupo(acc), user_id=USER_ID_GUARDIA)

    assert not ok
    filtro, cambio = mocks["cr"].update_one.call_args_list[-1].args
    assert cambio == {"$set": {f"answers.{acc.f['estatus_del_recorrido']}": "programado"}}
    assert not mocks["inbox"].called, "Quitó el rondín del inbox aunque no se asignó"


@pytest.mark.unit
@pytest.mark.target("claim_rondin")
def test_rondin_de_grupo_sin_padre_se_reclama_como_grupo(accesos_no_api, mocker):
    """
    TB-292: claim_rondin recibe el record_id que inicia la app; si el rondín
    es de grupo y no tiene padre, debe ir por el flujo de grupo
    (claim_group_rondin) con el usuario que lo inicia.
    """
    acc = accesos_no_api
    registro = rondin_de_grupo(acc)
    mocker.patch.object(acc, "get_record_by_id", return_value=registro)
    grupo = mocker.patch.object(acc, "claim_group_rondin", return_value=(True, {}))

    acc.claim_rondin(RONDIN_ID, user_id=USER_ID_GUARDIA)

    grupo.assert_called_once_with(registro, USER_ID_GUARDIA)


@pytest.mark.unit
@pytest.mark.target("claim_rondin")
def test_si_un_rondin_hermano_ya_no_esta_programado_no_se_reclama_nada(accesos_no_api, mocker):
    """
    TB-293: un rondín repartido en registros padre/hijos solo se puede
    reclamar si todos siguen 'programado'. Si otro guardia ya inició uno, se
    responde "ya fue reclamado" y no se cambia ningún registro.
    """
    acc = accesos_no_api
    hijo = {"_id": ObjectId(RONDIN_ID), "answers": {acc.rondin_keys["registro_padre"]: f"/records/detail/{PADRE_ID}"}}
    mocker.patch.object(acc, "get_record_by_id", side_effect=[hijo, {"_id": ObjectId(PADRE_ID), "answers": {}}])
    mocker.patch.object(acc, "_get_child_records", return_value=[hijo, {"_id": ObjectId(HERMANO_ID), "answers": {}}])
    mocker.patch.object(acc, "_extract_record_id_from_url", return_value=PADRE_ID)
    cr = mocker.MagicMock()
    cr.find.return_value = [{"_id": ObjectId(RONDIN_ID)}]   # solo 1 de 3 sigue programado
    mocker.patch.object(acc, "cr", cr)
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value=dict(PATCH_OK))

    ok, msg = acc.claim_rondin(RONDIN_ID, user_id=USER_ID_GUARDIA)

    assert not ok and "reclamado" in msg
    assert not cr.update_many.called and not cr.update_one.called, "Cambió registros de un rondín ya reclamado"
    assert not guardar.called


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
