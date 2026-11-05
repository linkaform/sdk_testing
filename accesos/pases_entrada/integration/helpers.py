# coding: utf-8

"""
Helpers de las pruebas de integración de Pases de Entrada.
"""

from ..data.pases_entrada_data import LIMITE_LISTA, LINK_PASE_UPDATE


def pase_de_la_lista(acceso_obj, pase_id, nombre, tab_status=""):
    """Registro del pase tal como lo regresa get_my_pases (la fila de la tabla), o None."""
    lista = acceso_obj.get_my_pases(tab_status=tab_status, search_name=nombre, limit=LIMITE_LISTA)
    return next((p for p in lista["records"] if p["_id"] == pase_id), None)


def payload_editar_pase(acceso_obj, pase, cambios):
    """
    Payload de update_full_pass como lo arma el front al guardar la edición:
    la fila de la tabla (pases-entrada-columns.tsx y table.tsx) pasa por el
    formulario (update-full-pass.tsx) y el modal de confirmación
    (add-pass-modal-update.tsx). `cambios` = lo que el guardia cambió en el
    formulario: nombre, empresa, fecha_desde_visita y fecha_desde_hasta.
    """
    visita_a = [v["nombre"] for v in pase.get("visita_a") or [] if v.get("nombre")]
    areas = [
        {"nombre_area": a.get("nombre_area"), "commentario_area": a.get("commentario_area") or ""}
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
        "acompanantes_grupo": pase.get("acompanantes_grupo") or [],
    }
