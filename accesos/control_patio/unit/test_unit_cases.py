# coding: utf-8

"""Transportistas – Control de patio: registrar la llegada de un camión
(create_visit_transportista) y guardarlo en la bitácora de transportistas
(save_bitac_transportista_record: etapas, andén, remolques, contenedores,
materiales y desglose de empaque) sin tocar la cuenta.
Notion: TB-331 a TB-338.

Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS:
./lkf test corre este archivo cuando cambia alguna funcion de C10_TRIGGERS.
La seccion la sirve Sanic en prod (transportistas_sdk.py): los tests llevan
back("sanic") y en addons salen SKIPPED.
"""

from bson import ObjectId
import pytest

from ..data.control_patio_data import (
    ESTATUS_CARGA_DESCARGA,
    ESTATUS_TERMINADO,
    REGISTRO_CAMION,
    GUARDADO_PATIO_OK,
    ANDEN_UNIT,
    REMOLQUE_EXISTENTE,
    CONTENEDOR_NUEVO,
    MATERIALES_POR_LUGAR,
    SIN_CAMBIOS,
    DESGLOSE_EMPAQUE,
    LLEGADA_SIN_PASE,
    ESTATUS_ARRIBO,
    CREADO_PATIO_OK,
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["create_visit_transportista", "save_bitac_transportista_record"]


def answers_del_camion(acceso_obj, mocker, data):
    """Guarda el camión con el guardado simulado y regresa los answers que se mandaron."""
    guardar = mocker.patch.object(acceso_obj.lkf_api, "patch_multi_record", return_value=dict(GUARDADO_PATIO_OK))
    acceso_obj.save_bitac_transportista_record(REGISTRO_CAMION, data)
    guardar.assert_called_once()
    assert guardar.call_args.kwargs["record_id"] == [REGISTRO_CAMION]
    return guardar.call_args.kwargs["answers"]


@pytest.mark.unit
@pytest.mark.target("save_bitac_transportista_record")
def test_pasar_camion_a_carga_descarga_guarda_el_estatus_y_la_fecha_de_descarga(accesos_no_api, mocker):
    """
    TB-331: al mover el camión a "carga / descarga" en el Kanban,
    save_bitac_transportista_record debe guardar ese estatus y la fecha y hora
    de descarga, y no la de terminado. Sin la fecha, el reporte no sabe
    cuánto tardó la descarga.
    """
    acc = accesos_no_api
    f = acc.bitacora_transportista_fields

    answers = answers_del_camion(acc, mocker, {"estatus": ESTATUS_CARGA_DESCARGA})

    assert answers[f["estatus"]] == ESTATUS_CARGA_DESCARGA
    assert answers.get(f["fecha_hora_descarga"]), "No se guardó la fecha de descarga"
    assert f["fecha_hora_terminado"] not in answers


@pytest.mark.unit
@pytest.mark.target("save_bitac_transportista_record")
def test_pasar_camion_a_terminado_guarda_la_fecha_de_terminado(accesos_no_api, mocker):
    """
    TB-332: al mover el camión a "terminado", save_bitac_transportista_record
    debe guardar ese estatus y la fecha y hora de terminado, y no volver a
    escribir la de descarga. Sin la fecha, no se sabe cuándo salió del patio.
    """
    acc = accesos_no_api
    f = acc.bitacora_transportista_fields

    answers = answers_del_camion(acc, mocker, {"estatus": ESTATUS_TERMINADO})

    assert answers[f["estatus"]] == ESTATUS_TERMINADO
    assert answers.get(f["fecha_hora_terminado"]), "No se guardó la fecha de terminado"
    assert f["fecha_hora_descarga"] not in answers


@pytest.mark.unit
@pytest.mark.target("save_bitac_transportista_record")
def test_asignar_anden_lo_guarda_en_el_camion(accesos_no_api, mocker):
    """
    TB-333: al asignar un andén desde el lápiz del Kanban,
    save_bitac_transportista_record debe guardarlo en el andén asignado del
    camión y nada más. Si no, el camión no aparece en el andén.
    """
    acc = accesos_no_api
    f = acc.bitacora_transportista_fields

    answers = answers_del_camion(acc, mocker, {"anden": ANDEN_UNIT})

    assert answers == {f["anden_asignado"]: ANDEN_UNIT}


@pytest.mark.unit
@pytest.mark.target("save_bitac_transportista_record")
def test_remolques_y_contenedores_se_guardan_en_el_mismo_grupo(accesos_no_api, mocker):
    """
    TB-334: remolques y contenedores van al mismo grupo del camión; el que ya
    existe se guarda en su renglón y el nuevo como renglón nuevo. El
    contenedor se guarda con su número de contenedor y el remolque con su
    número de caja. Si se cruzan, el detalle muestra la caja equivocada.
    """
    acc = accesos_no_api
    f = acc.bitacora_transportista_fields

    answers = answers_del_camion(
        acc, mocker, {"remolques": [dict(REMOLQUE_EXISTENTE)], "contenedores": [dict(CONTENEDOR_NUEVO)]}
    )

    grupo = answers[f["grupo_remolques"]]
    assert sorted(grupo) == [-2, 0], f"Renglones del grupo: {sorted(grupo)}"
    assert grupo[0][f["num_caja_contenedor"]] == REMOLQUE_EXISTENTE["no_caja"]
    assert grupo[-2][f["num_caja_contenedor"]] == CONTENEDOR_NUEVO["no_contenedor"]
    assert grupo[-2][f["num_sello"]] == CONTENEDOR_NUEVO["no_sello"]


@pytest.mark.unit
@pytest.mark.target("save_bitac_transportista_record")
def test_cada_material_se_guarda_con_su_lugar_segun_su_referencia(accesos_no_api, mocker):
    """
    TB-335: cada material del camión se guarda con su lugar según su
    referencia: contenedor, remolque o, sin referencia, vehículo. Si el lugar
    sale mal, la inspección de material busca el producto donde no está.
    """
    acc = accesos_no_api
    f = acc.bitacora_transportista_fields

    answers = answers_del_camion(acc, mocker, {"materiales": [dict(m) for m in MATERIALES_POR_LUGAR]})

    grupo = answers[f["grupo_materiales"]]
    lugares = [grupo[-(i + 1)][f["lugar_material"]] for i in range(len(MATERIALES_POR_LUGAR))]
    assert lugares == ["contenedor", "remolque", "vehiculo"], f"Lugares: {lugares}"


@pytest.mark.unit
@pytest.mark.target("save_bitac_transportista_record")
def test_guardar_el_camion_sin_cambios_no_llama_al_guardado(accesos_no_api, mocker):
    """
    TB-336: si el detalle del camión se guarda sin ningún cambio,
    save_bitac_transportista_record responde OK sin mandar nada a guardar. Un
    guardado vacío en LinkaForm solo genera una versión nueva del registro.
    """
    acc = accesos_no_api
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record")

    res = acc.save_bitac_transportista_record(REGISTRO_CAMION, dict(SIN_CAMBIOS))

    guardar.assert_not_called()
    assert res["status_code"] == 200


@pytest.mark.unit
@pytest.mark.target("save_bitac_transportista_record")
def test_el_desglose_de_empaque_reemplaza_el_grupo_completo(accesos_no_api, mocker):
    """
    TB-337: el front manda siempre el desglose de empaque completo. Se guarda
    reemplazando el grupo entero con lo que llega; si se agregara como
    renglones nuevos, el desglose se duplicaría en cada guardado.
    """
    acc = accesos_no_api
    f = acc.bitacora_transportista_fields
    cr = mocker.MagicMock()
    mocker.patch.object(acc, "cr", cr)
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record")

    acc.save_bitac_transportista_record(REGISTRO_CAMION, {"desglose_empaque": [dict(d) for d in DESGLOSE_EMPAQUE]})

    cr.update_one.assert_called_once()
    filtro, cambio = cr.update_one.call_args.args
    assert filtro["_id"] == ObjectId(REGISTRO_CAMION)
    grupo = cambio["$set"][f"answers.{f['grupo_desglose_empaque']}"]
    referencias = [r[f["no_referencia_material_desglose"]] for r in grupo]
    assert referencias == [d["no_referencia_material"] for d in DESGLOSE_EMPAQUE]
    guardar.assert_not_called()


@pytest.mark.unit
@pytest.mark.target("create_visit_transportista")
def test_la_llegada_de_un_camion_sin_pase_lo_deja_en_arribo(accesos_no_api, mocker):
    """
    TB-338: un camión que llega sin pase (Nuevo Acceso Transportista) se crea
    en la bitácora en "arribo", con su fecha de ingreso y sus placas, para que
    aparezca en la primera columna del Kanban del patio.
    """
    acc = accesos_no_api
    f = acc.bitacora_transportista_fields
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value={})
    crear = mocker.patch.object(acc.lkf_api, "post_forms_answers", return_value=dict(CREADO_PATIO_OK))

    acc.create_visit_transportista(dict(LLEGADA_SIN_PASE))

    crear.assert_called_once()
    answers = crear.call_args.args[0]["answers"]
    assert answers[f["estatus"]] == ESTATUS_ARRIBO
    assert answers.get(f["fecha_hora_ingreso"]), "No se guardó la fecha de ingreso"
    assert answers[f["placas_de_vehiculo"]] == LLEGADA_SIN_PASE["vehiculo"]["placa"]
