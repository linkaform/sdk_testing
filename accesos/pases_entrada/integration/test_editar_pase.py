# coding: utf-8

"""
Editar el pase completo desde la tabla de pases (Editar → update-full-pass.tsx
→ add-pass-modal-update.tsx → update_full_pass).
Notion: TB-121, TB-158 y TB-159.
"""

import pytest

from .fixtures import *
from .helpers import pase_de_la_lista, payload_editar_pase, crear_pase, fecha_str, obtener_qr_hijos
from ..data.pases_entrada_data import (
    EDICION_NOMBRE_SUFIJO,
    EDICION_EMPRESA,
    EDICION_DIAS_DESDE,
    EDICION_DIAS_HASTA,
    EDICION_HORA_HASTA,
    ACOMPANANTES_PASE,
)


@pytest.mark.integration
def test_editar_pase_completo_guarda_los_cambios(acceso_obj, mock_pase_nuevo):
    """
    TB-121: al editar un pase y cambiar nombre, empresa y fechas, la lista
    debe mostrar los valores nuevos. No basta con que update_full_pass
    responda 2xx: si no los guarda, el guardia ve el pase con los datos
    viejos y el visitante entra con fechas que ya no son las acordadas.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_nuevo)
    pase = pase_de_la_lista(acceso_obj, pase_id, mock_pase_nuevo["nombre"])
    assert pase, f"El pase {pase_id} no aparece en la lista para editarlo"

    cambios = {
        "nombre": mock_pase_nuevo["nombre"] + EDICION_NOMBRE_SUFIJO,
        "empresa": EDICION_EMPRESA,
        "fecha_desde_visita": fecha_str(EDICION_DIAS_DESDE),
        "fecha_desde_hasta": f"{fecha_str(EDICION_DIAS_HASTA)[:10]} {EDICION_HORA_HASTA}",
    }
    res = acceso_obj.update_full_pass(
        payload_editar_pase(acceso_obj, pase, cambios),
        folio=pase["folio"],
        qr_code=pase_id,
        location=pase["ubicacion"],
    )
    assert res.get("status_code") in (200, 201, 202), f"No se pudo editar el pase: {res}"

    editado = pase_de_la_lista(acceso_obj, pase_id, cambios["nombre"])
    assert editado, f"El pase no aparece en la lista con el nombre nuevo '{cambios['nombre']}'"
    assert editado["empresa"] == cambios["empresa"], f"La empresa quedó '{editado['empresa']}'"
    assert editado["fecha_desde_visita"] == cambios["fecha_desde_visita"], (
        f"La fecha desde quedó '{editado['fecha_desde_visita']}'"
    )
    assert editado["fecha_desde_hasta"] == cambios["fecha_desde_hasta"], (
        f"La fecha hasta quedó '{editado['fecha_desde_hasta']}'"
    )


@pytest.mark.integration
def test_editar_pase_con_acompanantes_no_los_duplica(acceso_obj, mock_pase_con_acompanantes):
    """
    TB-158: al editar las fechas de un pase con acompañantes en proceso, el
    grupo debe conservar los mismos pases de acompañante y no crear otros.
    Antes cada edición creaba un pase nuevo por acompañante y dejaba los
    anteriores sueltos, así que el visitante aparecía duplicado (ticket
    2610-1369).
    """
    pase_id = crear_pase(acceso_obj, mock_pase_con_acompanantes)
    qr_antes = obtener_qr_hijos(acceso_obj, pase_id)
    assert len(qr_antes) == len(ACOMPANANTES_PASE), (
        f"El pase se creó con {len(qr_antes)} acompañantes, se mandaron {len(ACOMPANANTES_PASE)}"
    )
    pase = pase_de_la_lista(acceso_obj, pase_id, mock_pase_con_acompanantes["nombre"])
    assert pase, f"El pase {pase_id} no aparece en la lista para editarlo"

    cambios = {
        "nombre": pase["nombre"],
        "empresa": pase["empresa"],
        "fecha_desde_visita": fecha_str(EDICION_DIAS_DESDE),
        "fecha_desde_hasta": f"{fecha_str(EDICION_DIAS_HASTA)[:10]} {EDICION_HORA_HASTA}",
    }
    res = acceso_obj.update_full_pass(
        payload_editar_pase(acceso_obj, pase, cambios),
        folio=pase["folio"],
        qr_code=pase_id,
        location=pase["ubicacion"],
    )
    assert res.get("status_code") in (200, 201, 202), f"No se pudo editar el pase: {res}"

    qr_despues = obtener_qr_hijos(acceso_obj, pase_id)
    assert sorted(qr_despues) == sorted(qr_antes), (
        f"Los acompañantes cambiaron al editar: antes {qr_antes}, después {qr_despues}"
    )


@pytest.mark.integration
def test_editar_fechas_del_titular_las_heredan_sus_acompanantes(acceso_obj, mock_pase_con_acompanantes):
    """
    TB-159: al cambiar las fechas de un pase con acompañantes, el pase de cada
    acompañante debe quedar con las mismas fechas. Si no las heredan, el
    titular entra en las fechas nuevas y sus acompañantes se quedan con las
    viejas (ticket 2610-1369).
    """
    pase_id = crear_pase(acceso_obj, mock_pase_con_acompanantes)
    qr_hijos = obtener_qr_hijos(acceso_obj, pase_id)
    assert len(qr_hijos) == len(ACOMPANANTES_PASE), (
        f"El pase se creó con {len(qr_hijos)} acompañantes, se mandaron {len(ACOMPANANTES_PASE)}"
    )
    pase = pase_de_la_lista(acceso_obj, pase_id, mock_pase_con_acompanantes["nombre"])
    assert pase, f"El pase {pase_id} no aparece en la lista para editarlo"

    cambios = {
        "nombre": pase["nombre"],
        "empresa": pase["empresa"],
        "fecha_desde_visita": fecha_str(EDICION_DIAS_DESDE),
        "fecha_desde_hasta": f"{fecha_str(EDICION_DIAS_HASTA)[:10]} {EDICION_HORA_HASTA}",
    }
    res = acceso_obj.update_full_pass(
        payload_editar_pase(acceso_obj, pase, cambios),
        folio=pase["folio"],
        qr_code=pase_id,
        location=pase["ubicacion"],
    )
    assert res.get("status_code") in (200, 201, 202), f"No se pudo editar el pase: {res}"

    for qr in qr_hijos:
        acompanante = acceso_obj.get_detail_access_pass(qr)
        assert acompanante.get("fecha_de_expedicion") == cambios["fecha_desde_visita"], (
            f"El acompañante {qr} quedó desde '{acompanante.get('fecha_de_expedicion')}'"
        )
        assert acompanante.get("fecha_de_caducidad") == cambios["fecha_desde_hasta"], (
            f"El acompañante {qr} quedó hasta '{acompanante.get('fecha_de_caducidad')}'"
        )
