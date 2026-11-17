"""Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS.

./lkf test corre SOLO este archivo cuando cambia alguna funcion de
C10_TRIGGERS. Aqui van los casos principales de cada funcion y las
validaciones mas importantes; los demas unitarios de la seccion viven en
otros archivos de unit/ y se corren a mano.
"""

import pytest
import copy
from ..data.concesionados_data import (
    LOCATION,
    OTRA_UBICACION,
    ESTADO_ABIERTO,
    ESTADO_TODOS,
    CONCESION_EMPLEADO,
    CONCESION_OTRO,
    EQUIPO_CONCESION,
    METADATA_CONCESION,
    GUARDADO_OK,
    COMENTARIO_PRESTAMO,
    FOTO_VALIDA,
    FOLIO_CONCESION,
    REGISTRO_CONCESION,
    MOVIMIENTO_EQUIPO,
    CANTIDAD_PRESTADA,
    ESTADO_DEVUELTO,
    DEVOLUCION_TOTAL,
    ESTADO_PARCIAL,
    devolucion_parcial,
)
from bson import ObjectId

C10_TRIGGERS = [
    "concesionados_base_match",
    "create_article_concessioned",
    "delete_article_concessioned",
    "update_article_concessioned",
]


def answers_guardados(acceso_obj, mocker, concesion):
    """Crea la concesión con el guardado simulado y regresa los answers que se mandaron."""
    mocker.patch.object(acceso_obj.lkf_api, "get_metadata", return_value=dict(METADATA_CONCESION))
    guardar = mocker.patch.object(acceso_obj.lkf_api, "post_forms_answers", return_value=dict(GUARDADO_OK))
    acceso_obj.create_article_concessioned(copy.deepcopy(concesion))
    return guardar.call_args.args[0]["answers"]


# --- concesionados base match ---
@pytest.mark.unit
def test_filtro_usa_la_ubicacion_y_el_estado_de_la_pestana(accesos_no_api):
    """
    TB-234: una ubicación en texto debe filtrar exacto por ella y la lista de
    ubicaciones del header con $in, ganando sobre la de texto. Pendientes
    manda el estado 'abierto' y debe entrar al filtro; Todos no filtra por
    estado. Si no, la lista mezcla concesiones de otras plantas o ya
    devueltas.
    """
    acc = accesos_no_api
    ubicacion = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID}.{acc.mf['ubicacion']}"
    estado = f"answers.{acc.cons_f['status_concesion']}"

    filtro = acc.concesionados_base_match(location=LOCATION, status=ESTADO_ABIERTO)
    assert filtro["form_id"] == acc.CONCESSIONED_ARTICULOS
    assert filtro["deleted_at"] == {"$exists": False}
    assert filtro[ubicacion] == LOCATION
    assert filtro[estado] == ESTADO_ABIERTO

    varias = acc.concesionados_base_match(location=LOCATION, locations=[LOCATION, OTRA_UBICACION])
    assert varias[ubicacion] == {"$in": [LOCATION, OTRA_UBICACION]}, f"Filtró {varias[ubicacion]!r}"

    todos = acc.concesionados_base_match(location=LOCATION, status=ESTADO_TODOS)
    assert estado not in todos, f"Todos filtró por estado {todos[estado]!r}"


# --- create article concessioned ---
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


# --- delete article concessioned ---
@pytest.mark.unit
def test_folio_que_no_existe_da_error_y_no_borra(accesos_no_api, mocker):
    """
    TB-235: si el folio no se encuentra, delete_article_concessioned debe
    detenerse con el error de folio no encontrado y no mandar a borrar nada.
    Si borra, el guardia no se entera de que la concesión que quería quitar
    no existía.
    """
    mocker.patch.object(accesos_no_api, "get_record_by_folio", return_value={})
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")

    with pytest.raises(Exception, match="No se encontro el folio correspondiente"):
        accesos_no_api.delete_article_concessioned([FOLIO_CONCESION])
    borrar.assert_not_called()


# --- update article concessioned (devoluciones) ---
def concesion_guardada(acceso_obj, estado=ESTADO_ABIERTO):
    """Registro de la concesión con un equipo en préstamo y sin devoluciones."""
    f = acceso_obj.cons_f
    return {
        "_id": ObjectId(REGISTRO_CONCESION),
        "folio": FOLIO_CONCESION,
        "answers": {
            f["status_concesion"]: estado,
            f["grupo_equipos"]: [{
                f["id_movimiento"]: MOVIMIENTO_EQUIPO,
                f["equipo_catalog_concesion"]: {f["_nombre_equipo"]: EQUIPO_CONCESION["nombre_equipo"]},
                f["cantidad_equipo_concesion"]: CANTIDAD_PRESTADA,
                f["cantidad_equipo_devuelto"]: 0,
                f["cantidad_equipo_pendiente"]: CANTIDAD_PRESTADA,
                f["status_concesion_equipo"]: ESTADO_ABIERTO,
            }],
        },
    }


def devolucion_simulada(acceso_obj, mocker, registro):
    """Simula el registro y el guardado; regresa el mock de patch_record."""
    mocker.patch.dict(acceso_obj.user, {"timezone": "America/Monterrey"})
    mocker.patch.object(acceso_obj, "get_record_by_id", return_value=registro)
    return mocker.patch.object(acceso_obj.lkf_api, "patch_record", return_value=dict(GUARDADO_OK))


@pytest.mark.unit
def test_concesion_ya_devuelta_no_se_vuelve_a_devolver(accesos_no_api, mocker):
    """
    TB-239: si la concesión ya está 'devuelto', update_article_concessioned
    debe detenerse con el error de que ya se encuentra devuelta y no guardar
    nada. Si guarda, la misma concesión suma devoluciones que no ocurrieron.
    """
    acc = accesos_no_api
    guardar = devolucion_simulada(acc, mocker, concesion_guardada(acc, ESTADO_DEVUELTO))

    with pytest.raises(Exception, match="ya se encuentra devuelta"):
        acc.update_article_concessioned({"status": "total", "state": "complete"}, REGISTRO_CONCESION)
    guardar.assert_not_called()


@pytest.mark.unit
def test_devolucion_total_sin_el_estado_del_equipo_da_error(accesos_no_api, mocker):
    """
    TB-240: una devolución total sin state (completo, dañado o perdido) debe
    detenerse con el error de que hay que indicar el estado y no guardar
    nada. Si guarda, no queda registro de en qué condición regresó el equipo.
    """
    acc = accesos_no_api
    guardar = devolucion_simulada(acc, mocker, concesion_guardada(acc))
    sin_estado = {k: v for k, v in DEVOLUCION_TOTAL.items() if k != "state"}

    with pytest.raises(Exception, match="hay que indicar el Estado"):
        acc.update_article_concessioned(sin_estado, REGISTRO_CONCESION)
    guardar.assert_not_called()


@pytest.mark.unit
def test_devolucion_total_deja_la_concesion_devuelta_con_fecha_de_cierre(accesos_no_api, mocker):
    """
    TB-241: con la devolución total de concesionados-nueva-devolucion,
    update_article_concessioned debe dejar cada equipo 'devuelto' con todo lo
    prestado devuelto y pendiente 0, poner la fecha de cierre y la concesión
    en 'devuelto'. Si queda algo pendiente, la concesión sigue en Pendientes.
    """
    acc = accesos_no_api
    guardar = devolucion_simulada(acc, mocker, concesion_guardada(acc))

    acc.update_article_concessioned(dict(DEVOLUCION_TOTAL), REGISTRO_CONCESION)

    guardar.assert_called_once()
    f = acc.cons_f
    answers = guardar.call_args.args[0]["answers"]
    assert answers[f["status_concesion"]] == ESTADO_DEVUELTO
    assert answers.get(f["fecha_cierre_concesion"]), "La concesión devuelta no tiene fecha de cierre"
    equipo = answers[f["grupo_equipos"]][0]
    assert equipo[f["status_concesion_equipo"]] == ESTADO_DEVUELTO
    assert equipo[f["cantidad_equipo_devuelto"]] == CANTIDAD_PRESTADA
    assert equipo[f["cantidad_equipo_pendiente"]] == 0
    devolucion = answers[f["grupo_equipos_devolucion"]][0]
    assert devolucion[f["id_movimiento_devolucion"]] == MOVIMIENTO_EQUIPO
    assert devolucion[f["cantidad_devolucion"]] == CANTIDAD_PRESTADA


@pytest.mark.unit
def test_devolver_parte_de_un_equipo_deja_la_concesion_parcial_con_el_pendiente_correcto(accesos_no_api, mocker):
    """
    TB-242: al devolver 1 de los 3 equipos prestados, update_article_concessioned
    debe dejar la concesión 'parcial' y en ese equipo 1 devuelto y 2
    pendientes. Si las cuentas no cuadran, Parciales muestra otra cantidad por
    devolver.
    """
    acc = accesos_no_api
    guardar = devolucion_simulada(acc, mocker, concesion_guardada(acc))

    acc.update_article_concessioned(devolucion_parcial(1), REGISTRO_CONCESION)

    guardar.assert_called_once()
    f = acc.cons_f
    answers = guardar.call_args.args[0]["answers"]
    assert answers[f["status_concesion"]] == ESTADO_PARCIAL
    equipo = answers[f["grupo_equipos"]][0]
    assert equipo[f["cantidad_equipo_devuelto"]] == 1
    assert equipo[f["cantidad_equipo_pendiente"]] == CANTIDAD_PRESTADA - 1
    assert answers[f["grupo_equipos_devolucion"]][0][f["cantidad_devolucion"]] == 1


@pytest.mark.unit
def test_devolver_mas_de_lo_que_falta_da_error_y_no_guarda(accesos_no_api, mocker):
    """
    TB-243: si se devuelven más equipos de los que faltan (4 de 3 prestados),
    update_article_concessioned debe detenerse con el aviso de devolución
    negativa y no guardar nada. Si guarda, el pendiente queda en negativo.
    """
    acc = accesos_no_api
    guardar = devolucion_simulada(acc, mocker, concesion_guardada(acc))

    with pytest.raises(Exception, match="negativa de: -1"):
        acc.update_article_concessioned(devolucion_parcial(CANTIDAD_PRESTADA + 1), REGISTRO_CONCESION)
    guardar.assert_not_called()
