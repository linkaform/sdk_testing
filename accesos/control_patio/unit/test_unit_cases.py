# coding: utf-8

"""Transportistas – Control de patio: guardar el camión en la bitácora de
transportistas (save_bitac_transportista_record: etapas, andén, remolques,
contenedores y materiales) sin tocar la cuenta.
Notion: TB-331 a TB-338.

Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS:
./lkf test corre este archivo cuando cambia alguna funcion de C10_TRIGGERS.
La seccion la sirve Sanic en prod (transportistas_sdk.py): los tests llevan
back("sanic") y en addons salen SKIPPED.
"""

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
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["save_bitac_transportista_record"]


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
