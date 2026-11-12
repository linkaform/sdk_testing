# coding: utf-8

"""
Helpers de las pruebas de integración de Pases de Entrada. Crear, completar y
cancelar pases, sacar a sus acompañantes y dar salida también los usan las
demás secciones (from pases_entrada.integration.helpers import crear_pase).
Todas pegan contra la API/BD real a través de `acceso_obj`.
"""

from datetime import datetime, timedelta

from pytz import timezone

from ..data.datos_base import FOTO_VALIDA, IDENTIFICACION_VALIDA
from ..data.pases_entrada_data import LIMITE_LISTA, LINK_PASE_UPDATE, ESTATUS_PROCESO


def pase_de_la_lista(acceso_obj, pase_id, nombre, tab_status=""):
    """Registro del pase tal como lo regresa get_my_pases (la fila de la tabla), o None."""
    lista = acceso_obj.get_my_pases(tab_status=tab_status, search_name=nombre, limit=LIMITE_LISTA)
    return next((p for p in lista["records"] if p["_id"] == pase_id), None)


def acompanantes_del_formulario(pase):
    """
    Acompañantes que manda el formulario de edición (update-full-pass.tsx):
    solo los que siguen en proceso, cada uno con el id de su pase (qr_code);
    los activos no se mandan. Foto e identificación vacías no se mandan
    (normalizeImageField las deja en undefined).
    """
    acompanantes = []
    for a in pase.get("acompanantes_grupo") or []:
        if (a.get("estatus") or "").lower() != ESTATUS_PROCESO:
            continue
        miembro = {
            "id": a.get("qr_code") or "",
            "nombre": a.get("nombre_acompanante") or "",
            "email": a.get("email_acompanante") or "",
            "telefono": a.get("telefono_acompanante") or "",
            "estatus": a.get("estatus") or "",
            "link": a.get("link") or "",
        }
        for llave in ("foto", "identificacion"):
            if a.get(llave):
                miembro[llave] = a[llave]
        acompanantes.append(miembro)
    return acompanantes


def payload_editar_pase(acceso_obj, pase, cambios):
    """
    Payload de update_full_pass como lo arma el front al guardar la edición:
    la fila de la tabla (pases-entrada-columns.tsx y table.tsx) pasa por el
    formulario (update-full-pass.tsx) y el modal de confirmación
    (add-pass-modal-update.tsx). `cambios` = lo que el guardia cambió en el
    formulario: nombre, empresa, fecha_desde_visita y fecha_desde_hasta.
    """
    visita_a = [v["nombre"] for v in pase.get("visita_a") or [] if v.get("nombre")]
    # La lista regresa el área como note_booth; el formulario la toma de
    # nombre_area o, si no viene, de note_booth (areasFormateadas).
    areas = [
        {
            "nombre_area": a.get("nombre_area") or a.get("note_booth") or "",
            "commentario_area": a.get("commentario_area") or "",
        }
        for a in pase.get("grupo_areas_acceso") or []
    ]
    telefono = pase.get("telefono") or ""
    if not telefono.startswith("+"):
        telefono = f"+52{telefono}"
    return {
        "created_from": "web",
        "nombre_pase": cambios["nombre"],
        "email_pase": pase.get("email") or "",
        "empresa_pase": cambios["empresa"],
        "telefono_pase": telefono,
        "ubicacion": [u for u in pase.get("ubicacion") or [] if u],
        "tema_cita": pase.get("tema_cita") or "",
        "descripcion": pase.get("descripcion") or "",
        "perfil_pase": pase.get("tipo_de_pase") or "",
        "status_pase": pase.get("estatus") or "",
        "visita_a": visita_a,
        "link": {
            "link": LINK_PASE_UPDATE,
            "docs": [],
            "qr_code": pase["_id"],
            "creado_por_id": acceso_obj.user.get("user_id", 0),
            "creado_por_email": acceso_obj.user.get("email", ""),
        },
        "qr_pase": pase.get("qr_pase") or [],
        "tipo_visita": "alta_de_nuevo_visitante",
        "enviar_correo_pre_registro": pase.get("enviar_correo_pre_registro") or [],
        "tipo_visita_pase": pase.get("tipo_fechas_pase") or "",
        "fecha_desde_visita": cambios["fecha_desde_visita"],
        "fecha_desde_hasta": cambios["fecha_desde_hasta"],
        "config_dia_de_acceso": pase.get("config_dia_de_acceso") or "cualquier_día",
        "config_dias_acceso": pase.get("limitado_a_dias") or [],
        "config_limitar_acceso": int(pase.get("limite_de_acceso") or 0) or 1,
        "grupo_areas_acceso": areas,
        "grupo_instrucciones_pase": pase.get("comentarios") or [],
        "grupo_vehiculos": pase.get("grupo_vehiculos") or [],
        "grupo_equipos": pase.get("grupo_equipos") or [],
        "autorizado_por": acceso_obj.user.get("email", ""),
        "walkin_fotografia": pase.get("foto") or [],
        "walkin_identificacion": pase.get("identificacion") or [],
        "enviar_correo": [],
        "habilitar_vehiculo": "sí" if pase.get("habilitar_vehiculo") in ("sí", True) else "no",
        "acompanantes": int(pase.get("acompanantes") or 0),
        "acompanantes_grupo": acompanantes_del_formulario(pase),
    }

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
