"""Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS.

./lkf test corre SOLO este archivo cuando cambia alguna funcion de
C10_TRIGGERS. Aqui van los casos principales de cada funcion y las
validaciones mas importantes; los demas unitarios de la seccion viven en
otros archivos de unit/ y se corren a mano.
"""

import pytest
from lkf_back import de
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
    ARTICULO_UNIT,
    EMPLEADO_PERDIDOS,
    GUARDADO_OK,
    TIPO_ARTICULO,
    ARTICULO_SELECCION,
    DEVOLUCION,
    ESTATUS_ENTREGADO,
    EDICION_OK,
)

C10_TRIGGERS = [
    "catalogo_tipo_articulo",
    "create_article_lost",
    "delete_article_lost",
    "perdidos_base_match",
    "update_article_lost",
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


def registrar_simulado(acc, mocker):
    """Simula el empleado y el guardado; regresa el mock de post_forms_answers."""
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value={})
    mocker.patch.object(de(acc, "get_employee_data"), "get_employee_data", return_value=dict(EMPLEADO_PERDIDOS))
    return mocker.patch.object(acc.lkf_api, "post_forms_answers", return_value=dict(GUARDADO_OK))


@pytest.mark.unit
def test_registrar_articulo_guarda_la_ubicacion_y_la_caseta_juntas(accesos_no_api, mocker):
    """
    TB-229: con ubicación y caseta, create_article_lost debe guardar las dos
    en el catálogo de ubicaciones del artículo. Si se pierde una, el artículo
    no aparece al filtrar por ella.
    """
    acc = accesos_no_api
    guardar = registrar_simulado(acc, mocker)

    acc.create_article_lost(dict(ARTICULO_UNIT))

    f = acc.perdidos_fields
    answers = guardar.call_args.args[0]["answers"]
    assert answers[f["ubicacion_catalog"]] == {f["ubicacion_perdido"]: LOCATION, f["area_perdido"]: AREA}


@pytest.mark.unit
def test_registrar_articulo_guarda_la_categoria_y_el_articulo_juntos(accesos_no_api, mocker):
    """
    TB-230: con categoría y artículo del catálogo, create_article_lost debe
    guardar los dos en el catálogo de tipos de artículo. Si se pierde uno, el
    buscador no lo encuentra por categoría o por artículo.
    """
    acc = accesos_no_api
    guardar = registrar_simulado(acc, mocker)

    acc.create_article_lost(dict(ARTICULO_UNIT))

    f = acc.perdidos_fields
    answers = guardar.call_args.args[0]["answers"]
    assert answers[f["tipo_articulo_catalog"]] == {
        f["tipo_articulo_perdido"]: TIPO_ARTICULO,
        f["articulo_seleccion"]: ARTICULO_SELECCION,
    }


def editar_simulado(acc, mocker):
    """Simula el empleado y el guardado; regresa el mock de patch_multi_record."""
    mocker.patch.object(de(acc, "get_employee_data"), "get_employee_data", return_value=dict(EMPLEADO_PERDIDOS))
    return mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value={**EDICION_OK, "json": {}})


@pytest.mark.unit
def test_entregar_articulo_lo_deja_entregado_con_fecha_y_quien_lo_recibe(accesos_no_api, mocker):
    """
    TB-231: con el payload de devolucion-article-modal y estatus 'entregado',
    update_article_lost debe guardar 'entregado', la fecha de entrega y los
    datos de quien lo recibe en el folio del artículo. Sin la fecha o sin quien
    lo recibe, no hay forma de saber cuándo ni a quién se le entregó.
    """
    acc = accesos_no_api
    guardar = editar_simulado(acc, mocker)

    res = acc.update_article_lost({**DEVOLUCION, "estatus_perdido": ESTATUS_ENTREGADO}, FOLIO_ARTICULO)

    guardar.assert_called_once()
    assert guardar.call_args.kwargs["folios"] == [FOLIO_ARTICULO]
    f = acc.perdidos_fields
    answers = guardar.call_args.kwargs["answers"]
    assert answers[f["estatus_perdido"]] == ESTATUS_ENTREGADO
    fecha_entrega = res["json"]["date_entrega_perdido"]
    assert fecha_entrega, "El artículo entregado no tiene fecha de entrega"
    assert answers[f["date_entrega_perdido"]] == fecha_entrega
    assert answers[f["recibe_perdido"]] == DEVOLUCION["recibe_perdido"]
    assert answers[f["telefono_recibe_perdido"]] == DEVOLUCION["telefono_recibe_perdido"]


@pytest.mark.unit
def test_editar_articulo_sin_entregarlo_lo_deja_pendiente_y_sin_fecha_de_entrega(accesos_no_api, mocker):
    """
    TB-233: con el payload de editar-article-modal (estatus 'pendiente'),
    update_article_lost debe guardar 'pendiente' en el folio del artículo y
    no ponerle fecha de entrega. Si le pone fecha, el artículo parece
    entregado aunque siga en Pendientes.
    """
    acc = accesos_no_api
    guardar = editar_simulado(acc, mocker)

    res = acc.update_article_lost(dict(ARTICULO_UNIT), FOLIO_ARTICULO)

    guardar.assert_called_once()
    assert guardar.call_args.kwargs["folios"] == [FOLIO_ARTICULO]
    f = acc.perdidos_fields
    answers = guardar.call_args.kwargs["answers"]
    assert answers[f["estatus_perdido"]] == ESTATUS_PENDIENTE
    assert f["date_entrega_perdido"] not in answers, "El artículo pendiente se guardó con fecha de entrega"
    assert res["json"]["date_entrega_perdido"] == ""


@pytest.mark.unit
def test_el_catalogo_de_articulos_se_pide_por_la_categoria_elegida(accesos_no_api, mocker):
    """
    TB-326: al elegir la categoría en + Nuevo Artículo, catalogo_tipo_articulo
    debe pedir al catálogo solo los artículos de esa categoría; sin categoría,
    el catálogo completo. Si el filtro se pierde, el select de artículo muestra
    los de todas las categorías.
    """
    acc = accesos_no_api
    consultar = mocker.patch.object(acc, "catalogo_view", return_value=[])

    acc.catalogo_tipo_articulo(TIPO_ARTICULO)
    acc.catalogo_tipo_articulo()

    por_categoria, completo = consultar.call_args_list
    assert por_categoria.args[:2] == (acc.TIPO_ARTICULOS_PERDIDOS_CAT_ID, acc.BITACORA_OBJETOS_PERDIDOS)
    opciones = por_categoria.args[2]
    assert opciones["startkey"] == [TIPO_ARTICULO]
    assert opciones["group_level"] == 2
    assert completo.args[2] == {}
