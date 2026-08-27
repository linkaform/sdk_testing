# coding: utf-8

"""
Datos de prueba para la batería de integración de do_access (incluye pase
grupal). El shape de `PASE_ACCESO_BASE` sigue el payload real que envía el
front al crear un pase (POST /scripts/run/ con option="create_access_pass"),
confirmado contra un curl real de Postman.

Nota: se omite deliberadamente `enviar_correo_pre_registro`/`enviar_sms_pre_registro`
para que correr esta batería no dispare correos/SMS reales a los datos de
contacto de prueba.
"""

LOCATION = "Planta Monterrey"
AREA = "Caseta Principal"

FOTO_VALIDA = [{
    "file_name": "imageUser.png",
    "file_url": "https://b2.linkaform.com/file/app-linkaform/public-client-126/71202/60b81349bde5588acca320e1/6a600482f4b892d898c9d603.png",
}]

IDENTIFICACION_VALIDA = [{
    "file_name": "imageCard.png",
    "file_url": "https://b2.linkaform.com/file/app-linkaform/public-client-126/71202/60b81349bde5588acca320e1/6a600480f4b892d898c9d602.png",
}]

PASE_ACCESO_BASE = {
    "created_from": "web",
    "selected_visita_a": "",
    "nombre": "Prueba do_access",
    "empresa": "Clave10",
    "email": "pruebas.do_access@clave10.com",
    "telefono": "+528110000000",
    "ubicaciones": [LOCATION],
    "tema_cita": "",
    "descripcion": "test do_access",
    "perfil_pase": "Visita General",
    "status_pase": "Proceso",
    "visita_a": ["Usuario Actual"],
    "custom": True,
    "link": {
        "link": "https://web.clave10.com/dashboard/pase-update",
        "docs": ["agregarIdentificacion", "agregarFoto"],
        "creado_por_id": 10,
        "creado_por_email": "seguridad@linkaform.com",
    },
    "tipo_visita_pase": "rango_de_fechas",
    "fechaFija": "",
    # fecha_desde_visita / fecha_desde_hasta se sobreescriben en el fixture
    # con fechas relativas a "hoy", ver helpers.fecha_str
    "fecha_desde_visita": "",
    "fecha_desde_hasta": "",
    "config_dia_de_acceso": "cualquier_día",
    "config_dias_acceso": [],
    "config_limitar_acceso": 0,
    "areas": [],
    "comentarios": [
        {"tipo_comentario": "pase", "comentario_pase": "pase de prueba do_access"}
    ],
    "todas_las_areas": True,
    "habilitar_vehiculo": "no",
}

ACOMPANANTE_UNO = {
    "nombre": "Acompañante Uno do_access",
    "email": "acompanante.uno.do_access@clave10.com",
    "telefono": "8110000001",
}

ACOMPANANTE_DOS = {
    "nombre": "Acompañante Dos do_access",
    "email": "acompanante.dos.do_access@clave10.com",
    "telefono": "8110000002",
}

DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
