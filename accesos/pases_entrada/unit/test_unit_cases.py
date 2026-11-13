"""Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS.

./lkf test corre SOLO este archivo cuando cambia alguna funcion de
C10_TRIGGERS. Aqui van los casos principales de cada funcion y las
validaciones mas importantes; los demas unitarios de la seccion viven en
otros archivos de unit/ y se corren a mano.
"""

import pytest
from .helpers import answers_pase, campos_pase_completo, fecha_hasta
from ..data.pases_entrada_data import (
    DIAS_VIGENTE,
    DIAS_VENCIDO,
    REQUIERE_FOTO_E_IDENTIFICACION,
    SIN_REQUERIMIENTOS,
    HABILITAR_SI,
    HABILITAR_NO,
    REQUIERE_IDENTIFICACION,
    NOMBRE_PASE_UNIT,
    AUTO_ACTIVACION_SI,
    AUTO_ACTIVACION_NO,
    URL_PADRE,
)

C10_TRIGGERS = [
    "_status_auto_activacion",
    "access_pass_set_status",
    "apply_habilitar_overrides",
]


# --- access pass set status ---
@pytest.mark.unit
def test_pase_completo_y_autorizado_queda_activo(accesos_no_api):
    """
    TB-197: con nombre, foto e identificación válidas (la ubicación las
    pide), fecha vigente, a quién visita y quién lo autorizó, el pase debe
    quedar 'activo'. Si no, un pase listo se queda esperando sin razón.
    """
    answers = answers_pase(accesos_no_api, **campos_pase_completo(accesos_no_api, DIAS_VIGENTE))

    estatus = accesos_no_api.access_pass_set_status(answers, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION)
    assert estatus == "activo", f"El pase completo y autorizado quedó {estatus!r}"


@pytest.mark.unit
def test_pase_completo_sin_autorizar_queda_por_autorizar(accesos_no_api):
    """
    TB-198: con todo completo pero sin quién lo autorizó (como un auto
    registro), el pase debe quedar 'por_autorizar'. Si queda activo, entra
    alguien que nadie aprobó.
    """
    campos = campos_pase_completo(accesos_no_api, DIAS_VIGENTE)
    campos.pop("catalago_autorizado_por")
    answers = answers_pase(accesos_no_api, **campos)

    estatus = accesos_no_api.access_pass_set_status(answers, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION)
    assert estatus == "por_autorizar", f"El pase sin autorizar quedó {estatus!r}"


@pytest.mark.unit
def test_pase_sin_la_foto_que_pide_la_ubicacion_queda_en_proceso(accesos_no_api):
    """
    TB-199: con todo completo y autorizado pero sin foto, en una ubicación
    que pide fotografía, el pase debe quedar en 'proceso' hasta que el
    visitante la suba. Si queda activo, entra sin la foto que la ubicación
    exige.
    """
    campos = campos_pase_completo(accesos_no_api, DIAS_VIGENTE)
    campos.pop("walkin_fotografia")
    answers = answers_pase(accesos_no_api, **campos)

    estatus = accesos_no_api.access_pass_set_status(answers, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION)
    assert estatus == "proceso", f"El pase sin foto quedó {estatus!r}"


@pytest.mark.unit
def test_ubicacion_sin_requerimientos_deja_activo_sin_foto_ni_identificacion(accesos_no_api):
    """
    TB-200: si la ubicación no pide foto ni identificación, un pase sin ellas
    pero con nombre, fecha vigente, a quién visita y autorizado debe quedar
    'activo'. Si queda en proceso, se queda ahí para siempre porque el link
    no le pide nada al visitante.
    """
    campos = campos_pase_completo(accesos_no_api, DIAS_VIGENTE)
    campos.pop("walkin_fotografia")
    campos.pop("walkin_identificacion")
    answers = answers_pase(accesos_no_api, **campos)

    estatus = accesos_no_api.access_pass_set_status(answers, requerimientos=SIN_REQUERIMIENTOS)
    assert estatus == "activo", f"El pase sin requisitos quedó {estatus!r}"


@pytest.mark.unit
def test_pase_con_fecha_hasta_en_el_pasado_queda_vencido(accesos_no_api):
    """
    TB-201: con la fecha hasta antes de hoy, el pase debe quedar 'vencido'
    aunque el resto esté completo. Si queda activo, entra alguien fuera de
    la vigencia que le dieron.
    """
    answers = answers_pase(accesos_no_api, **campos_pase_completo(accesos_no_api, DIAS_VENCIDO))

    estatus = accesos_no_api.access_pass_set_status(answers, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION)
    assert estatus == "vencido", f"El pase vencido quedó {estatus!r}"


# --- habilitar overrides ---
@pytest.mark.unit
def test_toggles_ganan_sobre_la_configuracion_de_la_ubicacion(accesos_no_api):
    """
    TB-196: en una ubicación que pide solo identificación, habilitar_fotografia
    "sí" debe agregar la foto y habilitar_identificacion "no" debe quitar la
    identificación. Sin los toggles se respeta lo que pide la ubicación. Si
    no, el pase pide (o se salta) datos que el admin decidió al crearlo.
    """
    toggles = {"habilitar_fotografia": HABILITAR_SI, "habilitar_identificacion": HABILITAR_NO}
    con_toggles = accesos_no_api.apply_habilitar_overrides(toggles, list(REQUIERE_IDENTIFICACION))
    assert sorted(con_toggles) == ["fotografia"], f"Con los toggles quedó {con_toggles}"

    sin_toggles = accesos_no_api.apply_habilitar_overrides({}, list(REQUIERE_IDENTIFICACION))
    assert sorted(sin_toggles) == REQUIERE_IDENTIFICACION, f"Sin los toggles quedó {sin_toggles}"


# --- status auto activacion ---
@pytest.mark.unit
def test_sin_auto_activacion_sigue_el_flujo_normal(accesos_no_api):
    """
    TB-192: con auto_activacion "no", o sin la llave, debe regresar None
    para que create_access_pass siga su flujo normal. Si regresa un estatus,
    el pase se activa aunque el anfitrión no lo pidió.
    """
    campos = {"walkin_nombre": NOMBRE_PASE_UNIT, "fecha_desde_hasta": fecha_hasta(accesos_no_api, DIAS_VIGENTE)}

    con_no = answers_pase(accesos_no_api, auto_activacion=AUTO_ACTIVACION_NO, **campos)
    assert accesos_no_api._status_auto_activacion(con_no, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION) is None

    sin_llave = answers_pase(accesos_no_api, **campos)
    assert accesos_no_api._status_auto_activacion(sin_llave, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION) is None


@pytest.mark.unit
def test_auto_activacion_deja_activo_sin_foto_ni_identificacion(accesos_no_api):
    """
    TB-193: con auto_activacion "sí", nombre y fecha vigente, el pase debe
    quedar 'activo' aunque la ubicación pida foto e identificación y no las
    traiga. Si queda en proceso, el guardia espera a un visitante que el
    anfitrión ya quería dejar pasar.
    """
    answers = answers_pase(
        accesos_no_api,
        auto_activacion=AUTO_ACTIVACION_SI,
        walkin_nombre=NOMBRE_PASE_UNIT,
        fecha_desde_hasta=fecha_hasta(accesos_no_api, DIAS_VIGENTE),
    )

    estatus = accesos_no_api._status_auto_activacion(answers, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION)
    assert estatus == "activo", f"El pase con auto activación quedó {estatus!r}"


@pytest.mark.unit
def test_acompanante_sin_nombre_se_queda_en_proceso(accesos_no_api):
    """
    TB-194: el pase de un acompañante (trae url_padre) hereda la auto
    activación del titular, pero sin nombre debe quedar en 'proceso' hasta
    que lo llenen. Si queda activo, hay un pase vigente sin saber de quién.
    """
    answers = answers_pase(
        accesos_no_api,
        auto_activacion=AUTO_ACTIVACION_SI,
        url_padre=URL_PADRE,
        walkin_nombre="",
        fecha_desde_hasta=fecha_hasta(accesos_no_api, DIAS_VIGENTE),
    )

    estatus = accesos_no_api._status_auto_activacion(answers, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION)
    assert estatus == "proceso", f"El acompañante sin nombre quedó {estatus!r}"


@pytest.mark.unit
def test_auto_activacion_no_reactiva_un_pase_vencido(accesos_no_api):
    """
    TB-195: con auto_activacion "sí" y la fecha hasta en el pasado, la fecha
    manda y el pase debe quedar 'vencido'. Si queda activo, entra alguien
    fuera de la vigencia que le dieron.
    """
    answers = answers_pase(
        accesos_no_api,
        auto_activacion=AUTO_ACTIVACION_SI,
        walkin_nombre=NOMBRE_PASE_UNIT,
        fecha_desde_hasta=fecha_hasta(accesos_no_api, DIAS_VENCIDO),
    )

    estatus = accesos_no_api._status_auto_activacion(answers, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION)
    assert estatus == "vencido", f"El pase vencido con auto activación quedó {estatus!r}"
