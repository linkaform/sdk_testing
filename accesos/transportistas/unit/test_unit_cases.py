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
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["create_pass_transportista"]


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
