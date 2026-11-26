# coding: utf-8

"""
Borrar un material desde el detalle del camión (save_bitac_transportista_record
con delete_materiales) sin tocar la cuenta: se simulan el camión de antes y el
guardado en Mongo, y se revisa cómo queda el grupo de materiales.
Notion: TB-419.
"""

import pytest

from ..data.control_patio_data import REGISTRO_CAMION, MATERIALES_INSPECCIONADOS

pytestmark = pytest.mark.back("sanic")


def test_borrar_un_material_conserva_la_evidencia_y_el_comentario_de_los_demas(accesos_no_api, mocker):
    """
    TB-419: al borrar un material, el back rearma el grupo de materiales con
    los que quedan; si deja fuera la evidencia y el comentario de la
    inspección, se borran de todos los demás materiales del camión.
    Ticket 2611-1666.
    """
    acc = accesos_no_api
    f = acc.bitacora_transportista_fields
    mocker.patch.object(acc, "get_bitac_transportista_record", return_value={"materiales": [dict(m) for m in MATERIALES_INSPECCIONADOS]})
    mongo = mocker.patch.object(acc, "cr")

    acc.save_bitac_transportista_record(REGISTRO_CAMION, {"delete_materiales": [0]})

    grupo = mongo.update_one.call_args.args[1]["$set"][f"answers.{f['grupo_materiales']}"]
    assert [m[f["producto_material"]] for m in grupo] == ["QA material que se queda"]
    queda = MATERIALES_INSPECCIONADOS[1]
    assert grupo[0].get(f["evidencia_material"]) == queda["evidencia"], "Se borró la evidencia del material que se queda"
    assert grupo[0].get(f["comentario_material"]) == queda["comentario"], "Se borró el comentario del material que se queda"
