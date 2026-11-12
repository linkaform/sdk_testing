# coding: utf-8

"""
Lista de pases (get_my_pases): pestañas Activos, Por autorizar, En Proceso y
Todos de la pantalla Pases de Entrada, su paginación y su buscador.
Notion: TB-111 a TB-116.
"""

import copy

import pytest

from .fixtures import *
from ..data.pases_entrada_data import (
    TAB_EN_PROCESO,
    TAB_TODOS,
    TAB_ACTIVOS,
    ESTATUS_PROCESO,
    ESTATUS_ACTIVO,
    PASE_COMPLETAR,
    TAB_POR_AUTORIZAR,
    ESTATUS_POR_AUTORIZAR,
    LIMITE_LISTA,
    FACET_NOMBRE,
    PASES_PARA_PAGINAR,
    LIMITE_PAGINA,
    PAGINAS_ESPERADAS,
)
from .helpers import crear_pase


@pytest.mark.integration
def test_pase_nuevo_de_web_aparece_en_proceso_y_no_en_activos(acceso_obj, mock_pase_nuevo):
    """
    TB-111: un pase creado desde + Nuevo Pase sin auto activación y sin
    requisitos de foto o identificación queda en 'proceso'. Debe aparecer en
    la pestaña En Proceso y no en Activos; si sale en Activos, el guardia lo
    trata como listo aunque el visitante no lo ha completado.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_nuevo)
    nombre = mock_pase_nuevo["nombre"]

    en_proceso = acceso_obj.get_my_pases(tab_status=TAB_EN_PROCESO, search_name=nombre, limit=LIMITE_LISTA)
    pases_en_proceso = {p["_id"]: p for p in en_proceso["records"]}
    assert pase_id in pases_en_proceso, "El pase nuevo no aparece en En Proceso"
    assert pases_en_proceso[pase_id].get("estatus") == ESTATUS_PROCESO, (
        f"El pase quedó '{pases_en_proceso[pase_id].get('estatus')}'"
    )

    activos = acceso_obj.get_my_pases(tab_status=TAB_ACTIVOS, search_name=nombre, limit=LIMITE_LISTA)
    assert pase_id not in {p["_id"] for p in activos["records"]}, "El pase en proceso aparece en Activos"


@pytest.mark.integration
def test_completar_pase_lo_pasa_de_en_proceso_a_activos(acceso_obj, mock_pase_nuevo):
    """
    TB-112: cuando el visitante completa su pase en pase-update (foto,
    identificación y aviso de privacidad, con el payload del modal de
    confirmación), el pase debe pasar a 'activo': aparecer en Activos y salir
    de En Proceso. Si se queda en proceso, el visitante no puede entrar
    aunque ya cumplió los requisitos.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_nuevo)
    nombre = mock_pase_nuevo["nombre"]

    completar = copy.deepcopy(PASE_COMPLETAR)
    completar.update({
        "nombre": nombre,
        "email": mock_pase_nuevo["email"],
        "telefono_pase": mock_pase_nuevo["telefono"],
    })
    res = acceso_obj.update_pass(completar, pase_id)
    assert res.get("status_code") in (200, 201, 202), f"No se pudo completar el pase: {res}"

    activos = acceso_obj.get_my_pases(tab_status=TAB_ACTIVOS, search_name=nombre, limit=LIMITE_LISTA)
    pases_activos = {p["_id"]: p for p in activos["records"]}
    assert pase_id in pases_activos, "El pase completado no aparece en Activos"
    assert pases_activos[pase_id].get("estatus") == ESTATUS_ACTIVO, (
        f"El pase completado quedó '{pases_activos[pase_id].get('estatus')}'"
    )

    en_proceso = acceso_obj.get_my_pases(tab_status=TAB_EN_PROCESO, search_name=nombre, limit=LIMITE_LISTA)
    assert pase_id not in {p["_id"] for p in en_proceso["records"]}, "El pase completado sigue en En Proceso"


@pytest.mark.integration
def test_pase_de_auto_registro_completo_cae_en_por_autorizar(acceso_obj, mock_pase_auto_registro):
    """
    TB-113: un visitante que se registra solo (auto registro) con foto e
    identificación deja un pase completo pero sin autorizar. Debe aparecer
    en la pestaña Por autorizar y no en Activos; si sale en Activos, entra
    sin que nadie lo haya autorizado.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_auto_registro)
    nombre = mock_pase_auto_registro["nombre"]

    por_autorizar = acceso_obj.get_my_pases(tab_status=TAB_POR_AUTORIZAR, search_name=nombre, limit=LIMITE_LISTA)
    pases_por_autorizar = {p["_id"]: p for p in por_autorizar["records"]}
    assert pase_id in pases_por_autorizar, "El pase de auto registro no aparece en Por autorizar"
    assert pases_por_autorizar[pase_id].get("estatus") == ESTATUS_POR_AUTORIZAR, (
        f"El pase de auto registro quedó '{pases_por_autorizar[pase_id].get('estatus')}'"
    )

    activos = acceso_obj.get_my_pases(tab_status=TAB_ACTIVOS, search_name=nombre, limit=LIMITE_LISTA)
    assert pase_id not in {p["_id"] for p in activos["records"]}, "El pase sin autorizar aparece en Activos"


@pytest.mark.integration
def test_todos_trae_pases_de_cualquier_estatus(acceso_obj, mock_pase_nuevo, pase_completado):
    """
    TB-114: la pestaña Todos no filtra por estatus. Con un pase en proceso y
    otro activo del mismo nombre, Todos debe traer los dos, cada uno con su
    estatus; si falta uno, el guardia no encuentra el pase en la lista general.
    """
    # Copia: el fixture pase_completado ya creó un pase con este mismo mock.
    pase_en_proceso = crear_pase(acceso_obj, copy.deepcopy(mock_pase_nuevo))

    todos = acceso_obj.get_my_pases(tab_status=TAB_TODOS, search_name=mock_pase_nuevo["nombre"], limit=LIMITE_LISTA)
    pases = {p["_id"]: p for p in todos["records"]}

    assert pase_en_proceso in pases, "El pase en proceso no aparece en Todos"
    assert pase_completado in pases, "El pase activo no aparece en Todos"
    assert pases[pase_en_proceso].get("estatus") == ESTATUS_PROCESO
    assert pases[pase_completado].get("estatus") == ESTATUS_ACTIVO


@pytest.mark.integration
def test_paginacion_de_pases_no_repite_ni_pierde_pases(acceso_obj, pases_para_paginar):
    """
    TB-115: la lista de pases pagina con limit/skip y el buscador del front
    (facets). Con 3 pases y 2 por página, las dos páginas deben traer los 3
    pases sin repetir ninguno, con el mismo total en las dos y la página
    actual que corresponde a skip. Si se repiten o se pierden, el guardia no
    encuentra un pase aunque exista.
    """
    nombre, ids = pases_para_paginar
    facets = [{"key": FACET_NOMBRE, "values": [nombre], "exact": False}]

    pagina_1 = acceso_obj.get_my_pases(tab_status=TAB_TODOS, limit=LIMITE_PAGINA, skip=0, facets=facets)
    pagina_2 = acceso_obj.get_my_pases(tab_status=TAB_TODOS, limit=LIMITE_PAGINA, skip=LIMITE_PAGINA, facets=facets)
    ids_1 = {p["_id"] for p in pagina_1["records"]}
    ids_2 = {p["_id"] for p in pagina_2["records"]}

    assert pagina_1["total_records"] == pagina_2["total_records"] == PASES_PARA_PAGINAR, (
        f"Totales: {pagina_1['total_records']} y {pagina_2['total_records']}, se crearon {PASES_PARA_PAGINAR}"
    )
    assert pagina_1["total_pages"] == PAGINAS_ESPERADAS, f"total_pages = {pagina_1['total_pages']}"
    assert (pagina_1["actual_page"], pagina_2["actual_page"]) == (1, 2)
    assert pagina_1["records_on_page"] == LIMITE_PAGINA
    assert pagina_2["records_on_page"] == PASES_PARA_PAGINAR - LIMITE_PAGINA
    assert not ids_1 & ids_2, f"Pases repetidos entre páginas: {ids_1 & ids_2}"
    assert ids_1 | ids_2 == ids, f"Faltan pases en las páginas: {ids - (ids_1 | ids_2)}"


@pytest.mark.integration
def test_buscador_de_pases_encuentra_el_pase_por_nombre(acceso_obj, mock_pase_nombre_unico):
    """
    TB-116: el buscador de la lista ofrece el campo Visitante (nombre) y,
    al escribir el nombre de un pase, cuenta y trae ese pase. Si no, el
    guardia no lo encuentra aunque exista.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_nombre_unico)
    nombre = mock_pase_nombre_unico["nombre"]

    campos = {c["key"]: c for c in acceso_obj.get_search_fields_pases()}
    assert FACET_NOMBRE in campos, f"El buscador no ofrece el campo '{FACET_NOMBRE}': {sorted(campos)}"
    assert campos[FACET_NOMBRE]["type"] == "text"

    candidato = {"key": FACET_NOMBRE, "value": nombre, "exact": False}
    conteo = acceso_obj.get_search_counts_pases(tab_status=TAB_TODOS, facets=[], candidates=[candidato])
    assert conteo == [1], f"El buscador cuenta {conteo} pases con el nombre '{nombre}'"

    facets = [{"key": FACET_NOMBRE, "values": [nombre], "exact": False}]
    lista = acceso_obj.get_my_pases(tab_status=TAB_TODOS, limit=LIMITE_LISTA, facets=facets)
    assert [p["_id"] for p in lista["records"]] == [pase_id], (
        f"El buscador trae {[p['_id'] for p in lista['records']]}, se esperaba solo {pase_id}"
    )
