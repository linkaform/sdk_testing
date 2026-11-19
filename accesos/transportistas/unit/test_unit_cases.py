# coding: utf-8

"""Transportistas – Nuevo Pase: crear el pase (create_pass_transportista), el
link del transportista (generate_submit_token_transportista, validate_token)
y los datos que completa el transportista (update_information_transportista),
sin tocar la cuenta.
Notion: TB-123 y TB-339 a TB-342.

Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS:
./lkf test corre este archivo cuando cambia alguna funcion de C10_TRIGGERS.
La seccion la sirve Sanic en prod (transportistas_sdk.py): los tests llevan
back("sanic") y en addons salen SKIPPED.
"""

import copy

import pytest

from ..data.transportistas_data import (
    PASE_TRANSPORTISTA_UNIT,
    FECHA_ENTREGA,
    ANDEN_ENTREGA,
    PASE_ID,
    GUARDADO_OK,
    INFORMACION_TRANSPORTISTA_UNIT,
    FOTO_LICENCIA,
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["create_pass_transportista", "generate_submit_token_transportista", "update_information_transportista", "validate_token"]


@pytest.mark.unit
@pytest.mark.target("create_pass_transportista")
def test_crear_pase_de_transportista_deja_un_registro_programado_en_el_patio(accesos_no_api, mocker):
    """
    TB-123: al crear un pase de transportista, create_pass_transportista debe
    guardar el pase y crear en la bitácora de transportistas un registro
    'programado' ligado al pase, con la fecha y el andén de entrega. Sin ese
    registro, el camión no aparece en la columna Programados del patio.
    """
    acc = accesos_no_api
    bf = acc.bitacora_transportista_fields
    mocker.patch.object(acc.lkf_api, "get_metadata", side_effect=lambda *a, **k: {})
    mocker.patch.object(acc, "object_id", return_value=PASE_ID)
    mocker.patch.object(acc, "create_custom_qr", return_value=[])
    guardar = mocker.patch.object(acc.lkf_api, "post_forms_answers", side_effect=lambda *a, **k: dict(GUARDADO_OK))

    acc.create_pass_transportista(copy.deepcopy(PASE_TRANSPORTISTA_UNIT))

    assert guardar.call_count == 2, f"Se guardaron {guardar.call_count} registros, se esperaban el pase y el programado"
    programado = guardar.call_args_list[1].args[0]["answers"]
    assert programado[bf["estatus"]] == "programado"
    assert programado[bf["num_de_pase"]] == PASE_ID
    assert programado[bf["fecha_hora_ingreso"]] == f"{FECHA_ENTREGA} 00:00:00"
    assert programado[bf["anden_asignado"]] == ANDEN_ENTREGA


@pytest.mark.unit
@pytest.mark.target("generate_submit_token_transportista")
def test_generar_link_del_transportista_guarda_un_token_nuevo_en_el_pase(accesos_no_api, mocker):
    """
    TB-339: al generar el link para que el transportista complete sus datos,
    generate_submit_token_transportista debe guardar un token nuevo en el pase
    y regresarlo con el record_id. Si el token no se guarda, el link que
    recibe el transportista no valida.
    """
    acc = accesos_no_api
    f = acc.pass_fields_transportista
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value={"status_code": 202})

    res = acc.generate_submit_token_transportista(PASE_ID)

    guardar.assert_called_once()
    assert guardar.call_args.kwargs["record_id"] == [PASE_ID]
    assert guardar.call_args.kwargs["form_id"] == acc.PASE_ENTRADA_TRANSPORTISTA
    assert res["record_id"] == PASE_ID
    assert res["token"], "No se generó el token"
    assert guardar.call_args.kwargs["answers"] == {f["token_transportista"]: res["token"]}


@pytest.mark.unit
@pytest.mark.target("validate_token")
def test_validar_link_del_transportista_sin_record_id_o_token_da_error(accesos_no_api, mocker):
    """
    TB-340: validate_token sin record_id o sin token debe detenerse con el
    error de que se requieren los dos, sin consultar la base. Si sigue, un
    link incompleto podría abrir el formulario del transportista.
    """
    acc = accesos_no_api
    cr = mocker.MagicMock()
    mocker.patch.object(acc, "cr", cr, create=True)

    with pytest.raises(Exception, match="Se requiere record_id y token"):
        acc.validate_token(record_id=PASE_ID, token=None)
    with pytest.raises(Exception, match="Se requiere record_id y token"):
        acc.validate_token(record_id=None, token="token-qa")
    cr.aggregate.assert_not_called()


def informacion_guardada(acceso_obj, mocker, data):
    """Guarda lo que completa el transportista con el guardado simulado y regresa los answers."""
    guardar = mocker.patch.object(acceso_obj.lkf_api, "patch_multi_record", return_value={"status_code": 202})
    acceso_obj.update_information_transportista(copy.deepcopy(data))
    guardar.assert_called_once()
    assert guardar.call_args.kwargs["record_id"] == [PASE_ID]
    return guardar.call_args.kwargs["answers"]


@pytest.mark.unit
@pytest.mark.target("update_information_transportista")
def test_completar_datos_del_transportista_guarda_conductor_y_vehiculo(accesos_no_api, mocker):
    """
    TB-341: con lo que completa el transportista en su link,
    update_information_transportista debe guardar el nombre y la licencia del
    conductor y las placas y marca del vehículo en el pase. La foto de la
    licencia solo se guarda si trae URL; sin URL queda vacía. Si guarda una
    foto sin URL, el detalle del camión muestra una imagen rota.
    """
    acc = accesos_no_api
    f = acc.pass_fields_transportista

    answers = informacion_guardada(acc, mocker, INFORMACION_TRANSPORTISTA_UNIT)

    conductor = INFORMACION_TRANSPORTISTA_UNIT["conductor"]
    assert answers[f["conductor_nombre"]] == conductor["nombre"]
    assert answers[f["conductor_no_licencia"]] == conductor["licencia"]
    assert answers[f["conductor_foto_licencia"]] == [FOTO_LICENCIA]
    assert answers[f["ayudante_foto_licencia"]] == []
    assert answers[f["vehiculo_placas"]] == INFORMACION_TRANSPORTISTA_UNIT["vehiculo"]["placas"]
    assert answers[f["vehiculo_marca"]] == INFORMACION_TRANSPORTISTA_UNIT["vehiculo"]["marca"]
