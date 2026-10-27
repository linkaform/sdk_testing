# coding: utf-8

"""
Salidas (do_out) de la bitácora de Entradas & Salidas.
Notion: TB-055 a TB-062.

do_out no crea un registro nuevo: cambia el MISMO registro de la entrada a
tipo_registro='salida' y le llena fecha_salida y duracion.
"""

import copy
import re
import pytest
from bson.errors import InvalidId

from .fixtures import *
from ..data.bitacora_data import (
    LOCATION,
    AREA,
    UBICACION_INEXISTENTE,
    RECORD_ID_INVALIDO,
    EQUIPO_PRUEBA,
    DOCUMENTO_GAFETE,
    DURACION_REGEX,
)
from .helpers import (
    crear_pase,
    completar_pase_activo,
    dar_entrada,
    salida_silenciosa,
    gafete_y_locker_disponibles,
    ultima_visita,
)


@pytest.mark.integration
def test_do_out_registra_salida_en_el_mismo_registro(acceso_obj, pase_dentro):
    """
    TB-055: tras la entrada, do_out debe cambiar ese mismo registro a
    'salida' con fecha_salida y duracion. Si falla, la
    bitácora deja a la persona "dentro" o pierde cuánto tiempo estuvo.
    """
    folio, entrada = pase_dentro

    acceso_obj.do_out(folio, LOCATION, AREA)

    salida = ultima_visita(acceso_obj, folio)
    assert salida["_id"] == entrada["_id"], "do_out creó o modificó otro registro"
    assert salida["status_visita"] == "salida"
    assert salida["checkout_date"], "No se guardó fecha_salida"
    assert salida["checkout_date"] >= salida["checkin_date"]
    assert re.match(DURACION_REGEX, salida["duration"] or ""), f"Duración inválida: {salida['duration']}"


@pytest.mark.integration
def test_do_out_doble_salida_es_rechazada(acceso_obj, pase_dentro):
    """
    TB-056: una segunda salida sobre la misma visita debe rechazarse; si
    no, se sobreescribiría fecha_salida/duración de una visita ya cerrada.
    """
    folio, _ = pase_dentro
    acceso_obj.do_out(folio, LOCATION, AREA)
    primera = ultima_visita(acceso_obj, folio)

    with pytest.raises(Exception) as exc_info:
        acceso_obj.do_out(folio, LOCATION, AREA)
    assert "no se encuentra dentro" in str(exc_info.value)

    despues = ultima_visita(acceso_obj, folio)
    assert despues["checkout_date"] == primera["checkout_date"]


@pytest.mark.integration
def test_do_out_sin_entrada_previa_mensaje_claro(acceso_obj, pase_activo):
    """
    TB-057: un pase activo que nunca entró no puede salir. El rechazo debe
    explicar que no hay entrada; hoy se sospecha que responde
    'Este usuario ingreso en None y no puede salir en ...'.
    """
    with pytest.raises(Exception) as exc_info:
        acceso_obj.do_out(pase_activo, LOCATION, AREA)
    mensaje = str(exc_info.value)
    assert "None" not in mensaje, f"Mensaje confuso para un pase sin entrada: {mensaje}"


@pytest.mark.integration
def test_do_out_en_otra_ubicacion_es_rechazada(acceso_obj, pase_dentro):
    """
    TB-058: quien entró por LOCATION no puede salir por otra ubicación
    (caseta no multi-ubicación). El registro debe seguir en 'entrada'.
    """
    folio, _ = pase_dentro

    with pytest.raises(Exception) as exc_info:
        acceso_obj.do_out(folio, UBICACION_INEXISTENTE, AREA)
    assert "no puede salir en" in str(exc_info.value)

    assert ultima_visita(acceso_obj, folio)["status_visita"] == "entrada"


@pytest.mark.integration
@pytest.mark.parametrize("location, area, mensaje", [
    (None, AREA, "especificar una ubicacion"),
    (LOCATION, None, "especificar el area"),
])
def test_do_out_sin_ubicacion_o_area_es_rechazada(acceso_obj, pase_dentro, location, area, mensaje):
    """
    TB-059: do_out sin ubicación o sin área debe responder error y no
    tocar el registro; sin esos datos no se sabe por qué caseta salió.
    """
    folio, _ = pase_dentro

    with pytest.raises(Exception) as exc_info:
        acceso_obj.do_out(folio, location, area)
    assert mensaje in str(exc_info.value)

    assert ultima_visita(acceso_obj, folio)["status_visita"] == "entrada"


@pytest.mark.integration
def test_do_out_con_gafete_sin_devolver_es_rechazada(acceso_obj, pase_dentro):
    """
    TB-060: con un gafete asignado (flujo real del front: assing_gafete
    con status 'asignado'), do_out debe exigir que se devuelva antes de
    registrar la salida; si no, el gafete se queda 'En Uso' para siempre.
    """
    folio, entrada = pase_dentro
    gafete_id, locker_id = gafete_y_locker_disponibles(acceso_obj, LOCATION, AREA)
    if not gafete_id:
        pytest.skip(f"No hay gafete y locker 'Disponible' en {LOCATION} / {AREA} en esta cuenta")

    datos_gafete = {
        "gafete_id": gafete_id,
        "locker_id": locker_id,
        "ubicacion": LOCATION,
        "area": AREA,
        "documento": DOCUMENTO_GAFETE,
    }
    asignado = acceso_obj.assing_gafete(
        {**datos_gafete, "status_gafete": "asignado"}, entrada["_id"], "entrada"
    )
    assert asignado, "assing_gafete no regresó respuesta al asignar"

    try:
        with pytest.raises(Exception) as exc_info:
            acceso_obj.do_out(folio, LOCATION, AREA)
        assert "liberar el gafete" in str(exc_info.value)
        assert ultima_visita(acceso_obj, folio)["status_visita"] == "entrada"
    finally:
        # Devuelve el gafete para no dejarlo 'En Uso' en preprod.
        acceso_obj.assing_gafete(
            {**datos_gafete, "documento": "", "status_gafete": "entregado"}, entrada["_id"], "salida"
        )


@pytest.mark.integration
def test_do_out_con_record_id_de_otro_pase_es_rechazada(acceso_obj, pase_dentro, mock_pase_bitacora):
    """
    TB-061 (caso 1): do_out del pase A con el record_id de la visita del
    pase B no debe cerrar ninguna de las dos.
    """
    folio_a, _ = pase_dentro
    folio_b = crear_pase(acceso_obj, mock_pase_bitacora)
    completar_pase_activo(acceso_obj, folio_b)
    entrada_b = dar_entrada(acceso_obj, folio_b, LOCATION, AREA)

    try:
        with pytest.raises(Exception):
            acceso_obj.do_out(folio_a, LOCATION, AREA, record_id=entrada_b["_id"])
        assert ultima_visita(acceso_obj, folio_a)["status_visita"] == "entrada"
        assert ultima_visita(acceso_obj, folio_b)["status_visita"] == "entrada"
    finally:
        salida_silenciosa(acceso_obj, folio_b, LOCATION, AREA)


@pytest.mark.integration
def test_do_out_con_record_id_invalido_error_controlado(acceso_obj, pase_dentro):
    """
    TB-061 (caso 2): un record_id mal formado debe dar un error de
    validación, no una excepción interna de Mongo (bson InvalidId).
    """
    folio, _ = pase_dentro

    with pytest.raises(Exception) as exc_info:
        acceso_obj.do_out(folio, LOCATION, AREA, record_id=RECORD_ID_INVALIDO)
    assert not isinstance(exc_info.value, InvalidId), "do_out no valida el formato de record_id"


@pytest.mark.integration
@pytest.mark.xfail(
    reason="Bug confirmado: get_last_user_move ordena por updated_at; tras editar una visita "
           "cerrada, do_out la toma como último movimiento y responde 'El usuario no se encuentra "
           "dentro' aunque hay una entrada abierta.",
    strict=True,
)
def test_do_out_tras_editar_visita_anterior_cierra_la_entrada_abierta(acceso_obj, mock_pase_bitacora):
    """
    TB-062: get_last_user_move ordena por updated_at. Si se edita una
    visita ya cerrada (p. ej. agregarle un equipo), esa pasa a ser el
    "último movimiento" y do_out podría fallar aunque hay una entrada abierta.
    """
    # El pase necesita 2 entradas: create_access_pass convierte
    # config_limitar_acceso=0 en 1 (app.py:3161), así que se pide un límite explícito.
    pase = copy.deepcopy(mock_pase_bitacora)
    pase["config_limitar_acceso"] = 5
    folio = crear_pase(acceso_obj, pase)
    completar_pase_activo(acceso_obj, folio)

    # Visita 1: entra y sale.
    visita_1 = dar_entrada(acceso_obj, folio, LOCATION, AREA)
    acceso_obj.do_out(folio, LOCATION, AREA)

    # Visita 2: entra y se queda dentro.
    visita_2 = dar_entrada(acceso_obj, folio, LOCATION, AREA)
    assert visita_2["_id"] != visita_1["_id"]

    try:
        # Se edita la visita 1 (cerrada) después de abrir la visita 2.
        acceso_obj.update_bitacora_entrada(
            {"action": "create", "equipo": EQUIPO_PRUEBA}, record_id=visita_1["_id"]
        )

        acceso_obj.do_out(folio, LOCATION, AREA)

        visitas = {v["_id"]: v for v in acceso_obj.get_list_last_user_move(folio)}
        assert visita_2["_id"] in visitas, f"La visita {visita_2['_id']} no aparece en la bitácora"
        assert visitas[visita_2["_id"]]["status_visita"] == "salida"
    finally:
        # Con record_id para cerrar la visita 2 aunque el bug esté presente.
        salida_silenciosa(acceso_obj, folio, LOCATION, AREA, record_id=visita_2["_id"])
