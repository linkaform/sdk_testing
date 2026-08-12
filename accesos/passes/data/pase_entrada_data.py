# Payload real y funcional para create_access_pass() en preprod (cuenta 10).
# Los valores de catalogo (ubicacion, perfil_pase, visita_a) son validos
# para esta cuenta al dia de hoy; si el catalogo de preprod cambia, actualizar aqui.

PASE_ENTRADA = {
    "selected_visita_a": "",
    "nombre": "Pruebas Juan",
    "empresa": "Empresa de Pruebas",
    "email": "email@pruebas.com",
    "telefono": "+521234567890",
    "ubicacion": "Planta Monterrey",
    "ubicaciones": [
        "Planta Monterrey",
        "Planta Durango"
    ],
    "tema_cita": "Pruebas Automaticas",
    "descripcion": "Comentario de Pruebas",
    "perfil_pase": "Visita General",
    "status_pase": "Proceso",
    "visita_a": ["Emiliano Zapata"],
    "custom": True,
    "link": {
        "link": "https://web.clave10.com/dashboard/pase-update",
        "docs": [
            "agregarFoto",
            "agregarIdentificacion"
        ],
        "creado_por_id": 10,
        "creado_por_email": "seguridad@linkaform.com"
    },
    "enviar_correo_pre_registro": [
        "enviar_correo_pre_registro",
        "enviar_sms_pre_registro"
    ],
    "tipo_visita_pase": "rango_de_fechas",
    "fechaFija": "",
    "fecha_desde_visita": "",   # se sobreescribe en el test con la fecha de hoy
    "fecha_desde_hasta": "",    # se sobreescribe en el test con la fecha de hoy
    "config_dia_de_acceso": "cualquier_día",
    "config_dias_acceso": [],
    "config_limitar_acceso": 3,
    "areas": [],
    "comentarios": [],
    "enviar_pre_sms": {
        "from": "enviar_pre_sms",
        "mensaje": "SOY UN MENSAJE",
        "numero": "+521234567890"
    },
    "todas_las_areas": False,
    "created_from": "web"
}
