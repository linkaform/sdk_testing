# coding: utf-8

"""
Iniciar (reclamar) un rondín asignado a varios guardias: claim_rondin y
claim_group_rondin. Solo uno se lo debe quedar. Se simulan Mongo (self.cr),
LinkaForm y el inbox; se revisa qué se bloquea, qué se guarda y qué se quita.
Notion: TB-284 a TB-288 (pendientes de dar de alta).
"""

from types import SimpleNamespace

import pytest
from bson import ObjectId

from ..data.rondines_data import (
    USER_ID_GUARDIA,
    USUARIO_GUARDIA,
    RONDIN_ID,
    HERMANO_ID,
    PADRE_ID,
    PATCH_OK,
    PATCH_ERROR,
)

pytestmark = pytest.mark.back("sanic")


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
    TB-284: el guardia que inicia un rondín de grupo queda en "Asignado a",
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
    TB-285: si otro guardia ganó el rondín (el bloqueo no encuentra el
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
    TB-286: si LinkaForm rechaza la asignación, el rondín debe regresar a
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
    TB-287: claim_rondin recibe el record_id que inicia la app; si el rondín
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
    TB-288: un rondín repartido en registros padre/hijos solo se puede
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
