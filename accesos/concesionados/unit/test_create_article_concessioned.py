# coding: utf-8

"""
Crear una concesión (create_article_concessioned, + Nueva Concesión) sin
tocar preprod: se simula el guardado y se revisan los answers que se mandan
a la forma.
Notion: TB-236 a TB-238.
"""

import copy

import pytest
from bson import ObjectId

from ..data.concesionados_data import (
    CONCESION_EMPLEADO,
    CONCESION_OTRO,
    EQUIPO_CONCESION,
    METADATA_CONCESION,
    GUARDADO_OK,
    COMENTARIO_PRESTAMO,
    FOTO_VALIDA,
)


@pytest.mark.unit
def test_crear_concesion_sin_equipos_da_error_y_no_la_guarda(accesos_no_api, mocker):
    """
    TB-236: una concesión sin equipos debe detenerse con el error de que se
    requiere la lista de equipos y no guardarse. Si se guarda, queda una
    concesión que no presta nada y no se puede devolver.
    """
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "post_forms_answers")

    with pytest.raises(Exception, match="Se requiere enviar lista de equipos concesionados"):
        accesos_no_api.create_article_concessioned(dict(CONCESION_EMPLEADO))
    guardar.assert_not_called()


def answers_guardados(acceso_obj, mocker, concesion):
    """Crea la concesión con el guardado simulado y regresa los answers que se mandaron."""
    mocker.patch.object(acceso_obj.lkf_api, "get_metadata", return_value=dict(METADATA_CONCESION))
    guardar = mocker.patch.object(acceso_obj.lkf_api, "post_forms_answers", return_value=dict(GUARDADO_OK))
    acceso_obj.create_article_concessioned(copy.deepcopy(concesion))
    return guardar.call_args.args[0]["answers"]


@pytest.mark.unit
def test_concesion_nueva_nace_abierta_con_sus_equipos_abiertos(accesos_no_api, mocker):
    """
    TB-237: una concesión nueva debe guardarse 'abierto', con cada equipo
    'abierto' y su id de movimiento (con él se devuelve después). Si la pide
    un empleado se marca 'empleado'; si no, 'otro'. Si el equipo no tiene id
    de movimiento, no se puede devolver.
    """
    campos = accesos_no_api.cons_f

    answers = answers_guardados(accesos_no_api, mocker, {**CONCESION_EMPLEADO, "equipos": [EQUIPO_CONCESION]})
    assert answers[campos["status_concesion"]] == "abierto"
    assert answers[campos["tipo_persona_solicita"]] == "empleado"
    equipos = answers[campos["grupo_equipos"]]
    assert len(equipos) == 1, f"Se guardaron {len(equipos)} equipos, se mandó 1"
    assert equipos[0][campos["status_concesion_equipo"]] == "abierto"
    assert ObjectId.is_valid(equipos[0][campos["id_movimiento"]]), (
        f"El id de movimiento quedó {equipos[0][campos['id_movimiento']]!r}"
    )

    otro = answers_guardados(accesos_no_api, mocker, {**CONCESION_OTRO, "equipos": [EQUIPO_CONCESION]})
    assert otro[campos["tipo_persona_solicita"]] == "otro"


@pytest.mark.unit
def test_foto_y_comentario_del_prestamo_se_guardan_en_los_campos_del_prestamo(accesos_no_api, mocker):
    """
    TB-238: el front manda la foto y el comentario del préstamo con los
    nombres de Devoluciones (evidencia_entrega, comentario_entrega); deben
    guardarse en los campos del préstamo, y lo que no es del grupo de
    equipos (marca_equipo_concesion) debe descartarse. Si quedan en los de
    Devoluciones, LinkaForm no los muestra en el préstamo.
    """
    campos = accesos_no_api.cons_f

    answers = answers_guardados(accesos_no_api, mocker, {**CONCESION_EMPLEADO, "equipos": [EQUIPO_CONCESION]})

    equipo = answers[campos["grupo_equipos"]][0]
    assert equipo[campos["evidencia_prestamo"]] == FOTO_VALIDA
    assert equipo[campos["comentario_prestamo"]] == COMENTARIO_PRESTAMO
    assert campos["evidencia_entrega"] not in equipo, "La foto quedó en el campo de Devoluciones"
    assert campos["comentario_entrega"] not in equipo, "El comentario quedó en el campo de Devoluciones"
    assert campos["marca_equipo_concesion"] not in equipo, "Se guardó un campo que no es del grupo de equipos"
