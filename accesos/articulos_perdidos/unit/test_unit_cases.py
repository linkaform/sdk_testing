"""Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS.

./lkf test corre SOLO este archivo cuando cambia alguna funcion de
C10_TRIGGERS. Aqui van los casos principales de cada funcion y las
validaciones mas importantes; los demas unitarios de la seccion viven en
otros archivos de unit/ y se corren a mano.
"""

import pytest
from ..data.perdidos_data import (
    FOLIO_ARTICULO,
    FOLIOS_ARTICULO,
    REGISTROS_ARTICULO,
    URL_REGISTRO,
    BORRADO_OK,
    LOCATION,
    AREA,
    OTRA_UBICACION,
    ESTATUS_PENDIENTE,
    ESTATUS_TODOS,
)

C10_TRIGGERS = [
    "delete_article_lost",
    "perdidos_base_match",
]


# --- delete article lost ---
@pytest.mark.unit
def test_folio_que_no_existe_da_error_y_no_borra(accesos_no_api, mocker):
    """
    TB-226: si el folio no se encuentra, delete_article_lost debe detenerse
    con el error de folio no encontrado y no mandar a borrar nada. Si borra,
    el guardia no se entera de que el artículo que quería quitar no existía.
    """
    mocker.patch.object(accesos_no_api, "get_record_by_folio", return_value={})
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")

    with pytest.raises(Exception, match="No se encontro el folio correspondiente"):
        accesos_no_api.delete_article_lost([FOLIO_ARTICULO])
    borrar.assert_not_called()


@pytest.mark.unit
def test_sin_folios_da_error_y_no_borra(accesos_no_api, mocker):
    """
    TB-227: con la lista de folios vacía, delete_article_lost debe detenerse
    con el error de lista vacía y no mandar a borrar nada.
    """
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")

    with pytest.raises(Exception, match="Lista de folios vacia"):
        accesos_no_api.delete_article_lost([])
    borrar.assert_not_called()


@pytest.mark.unit
def test_varios_articulos_manda_a_borrar_cada_registro(accesos_no_api, mocker):
    """
    TB-228: con dos folios, delete_article_lost debe mandar a borrar en una
    sola llamada el registro de cada uno, y ninguno más. Si falta uno, el
    artículo sigue en la lista; si sobra, se borra uno que el guardia no
    eligió.
    """
    mocker.patch.object(
        accesos_no_api, "get_record_by_folio", side_effect=lambda folio, *a, **k: {"_id": REGISTROS_ARTICULO[folio]}
    )
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")
    mocker.patch.object(accesos_no_api, "check_status_code", return_value=dict(BORRADO_OK))

    res = accesos_no_api.delete_article_lost(list(FOLIOS_ARTICULO))

    assert res == BORRADO_OK
    borrar.assert_called_once()
    esperados = [URL_REGISTRO.format(REGISTROS_ARTICULO[folio]) for folio in FOLIOS_ARTICULO]
    assert borrar.call_args.args[0] == {"deleted_objects": esperados}, f"Mandó a borrar {borrar.call_args.args[0]}"


# --- perdidos base match ---
@pytest.mark.unit
def test_filtro_toma_la_ubicacion_en_texto_o_en_lista(accesos_no_api):
    """
    TB-224: una ubicación en texto debe filtrar exacto por ella; la lista de
    ubicaciones del header debe filtrar con $in y ganar sobre la de texto.
    Sin ninguna no debe filtrar por ubicación. Si no, la lista trae
    artículos de otras plantas o ninguno.
    """
    acc = accesos_no_api
    ubicacion = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_SALIDA_OBJ_ID}.{acc.mf['ubicacion']}"

    filtro = acc.perdidos_base_match(location=LOCATION)
    assert filtro["form_id"] == acc.BITACORA_OBJETOS_PERDIDOS
    assert filtro["deleted_at"] == {"$exists": False}
    assert filtro[ubicacion] == LOCATION

    varias = acc.perdidos_base_match(location=LOCATION, locations=[LOCATION, OTRA_UBICACION])
    assert varias[ubicacion] == {"$in": [LOCATION, OTRA_UBICACION]}, f"Filtró {varias[ubicacion]!r}"

    sin_ubicacion = acc.perdidos_base_match()
    assert ubicacion not in sin_ubicacion, f"Sin ubicación filtró {sin_ubicacion[ubicacion]!r}"


@pytest.mark.unit
def test_filtro_usa_el_estatus_de_la_pestana_y_la_caseta(accesos_no_api):
    """
    TB-225: Pendientes manda el estatus 'pendiente' y la caseta; los dos
    deben entrar al filtro. Todos no manda estatus y no debe filtrar por
    estatus. Si no, Pendientes mezcla artículos ya entregados o Todos deja
    fuera algunos.
    """
    acc = accesos_no_api
    estatus = f"answers.{acc.perdidos_fields['estatus_perdido']}"
    caseta = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_SALIDA_OBJ_ID}.{acc.mf['nombre_area_salida']}"

    pendientes = acc.perdidos_base_match(location=LOCATION, area=AREA, status=ESTATUS_PENDIENTE)
    assert pendientes[estatus] == ESTATUS_PENDIENTE
    assert pendientes[caseta] == AREA

    todos = acc.perdidos_base_match(location=LOCATION, status=ESTATUS_TODOS)
    assert estatus not in todos, f"Todos filtró por estatus {todos[estatus]!r}"
