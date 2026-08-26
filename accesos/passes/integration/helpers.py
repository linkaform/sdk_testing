# coding: utf-8

"""
Helpers reutilizables para las pruebas de integración de pases/do_access.
Todas las funciones aquí pegan contra la API/BD real a través de `acceso_obj`
(ver README.md de la suite: la capa integration no mockea nada).
"""

from datetime import datetime, timedelta
from pytz import timezone

from .data.do_access_data import FOTO_VALIDA, IDENTIFICACION_VALIDA


def fecha_str(dias_offset=0, tz_name='America/Mexico_City'):
    """Fecha/hora actual +/- `dias_offset` días, en el formato que espera el pase."""
    tz = timezone(tz_name)
    fecha = datetime.now(tz) + timedelta(days=dias_offset)
    return fecha.strftime('%Y-%m-%d %H:%M:%S')


def crear_pase(acceso_obj, access_pass):
    """Crea un pase (create_access_pass) y devuelve su folio/record_id."""
    res = acceso_obj.create_access_pass(access_pass)
    assert res.get('status_code') == 201, f"No se pudo crear el pase: {res}"
    return res['json']['id']


def completar_pase_activo(acceso_obj, folio, visita_a=None):
    """
    Sube foto + identificación y llena visita_a para que
    access_pass_set_status marque el pase como 'activo'.
    """
    access_pass = {
        "walkin_fotografia": FOTO_VALIDA,
        "walkin_identificacion": IDENTIFICACION_VALIDA,
        "visita_a": visita_a or ["Usuario Actual"],
    }
    response = acceso_obj.update_pass(access_pass, folio)
    assert response.get('status_code') == 202, f"No se pudo completar el pase {folio}: {response}"
    detalle = acceso_obj.get_detail_access_pass(folio)
    assert detalle.get('estatus') == 'activo', (
        f"El pase {folio} no quedo activo, estatus={detalle.get('estatus')}"
    )
    return detalle


def cancelar_pase(acceso_obj, folio):
    """Marca el pase como cancelado vía update_pass."""
    response = acceso_obj.update_pass({"status_pase": "cancelado"}, folio)
    assert response.get('status_code') == 202, f"No se pudo cancelar el pase {folio}: {response}"
    return acceso_obj.get_detail_access_pass(folio)


def obtener_qr_hijos(acceso_obj, folio_padre):
    """Extrae el qr_code (ya hidratado por get_detail_access_pass) de cada acompañante."""
    detalle = acceso_obj.get_detail_access_pass(folio_padre)
    return [a['qr_code'] for a in (detalle.get('acompanantes_grupo') or []) if a.get('qr_code')]


def hacer_salida(acceso_obj, qr_code, location, area):
    """
    Registra la salida del pase para liberar la ubicación
    (validate_access_pass_location) y dejar el par entrada/salida completo.
    """
    return acceso_obj.do_out(qr_code, location, area)
