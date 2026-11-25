# coding: utf-8

"""
Datos de prueba para la sección Incidencias (Nueva incidencia, editar y
seguimientos; script incidencias_sdk.py de Sanic).
"""

from pases_entrada.data.datos_base import (  # noqa: F401
    LOCATION,
    AREA,
)

# Payload de add-incidencia.tsx (lib/incidencias.ts InputIncidencia) con lo
# que el formulario manda al crear: catálogo, ubicación y caseta, prioridad
# con mayúscula y "Reporta" vacío (lo pone el back con el guardia de la sesión).
INCIDENCIA_NUEVA = {
    "reporta_incidencia": "",
    "fecha_hora_incidencia": "2026-11-13 10:00:00",
    "ubicacion_incidencia": LOCATION,
    "area_incidencia": AREA,
    "categoria": "Seguridad",
    "sub_categoria": "",
    "incidencia": "Intrusión",
    "comentario_incidencia": "Incidencia de prueba QA",
    "prioridad_incidencia": "Alta",
    "evidencia_incidencia": [],
    "documento_incidencia": [],
}

# Guardia de la sesión que regresa _reporta_sesion.
GUARDIA_SESION = "Guardia de prueba QA"

# Respuestas simuladas de post_forms_answers / patch_forms_answers.
GUARDADO_OK = {"status_code": 201, "json": {"id": "6a0000000000000000000001"}}
GUARDADO_ERROR = {"status_code": 400, "json": {"error": "simulado"}}
EDITADO_OK = {"status_code": 202}

# "Reportar como falla" de add-incidencia.tsx: concepto y subconcepto de la falla.
REPORTAR_FALLA = {"concepto": "Puerta", "subconcepto": "Chapa"}

# Afectación patrimonial: una sin monto (el campo es decimal opcional) y una con monto.
AFECTACION_SIN_MONTO = {"tipo_afectacion": "Daño", "descripcion_afectacion": "Vidrio roto", "monto_estimado": ""}
AFECTACION_CON_MONTO = {"tipo_afectacion": "Daño", "descripcion_afectacion": "Puerta", "monto_estimado": "1500"}

# Editar: folio, la incidencia como estaba (lo que regresa _incidencia_formateada)
# y dos seguimientos: uno que ya existía (trae registrado_por) y uno nuevo.
FOLIO_INCIDENCIA = "731-10"
INCIDENCIA_ANTES = {"_id": "6a0000000000000000000001", "folio": FOLIO_INCIDENCIA, "estatus": "abierto"}
SEGUIMIENTO_EXISTENTE = {"accion_correctiva_incidencia": "Se revisó la cámara", "registrado_por": "Supervisor QA"}
SEGUIMIENTO_NUEVO = {"accion_correctiva_incidencia": "Se cambió la chapa"}

# Tiempo transcurrido al cierre: texto que ya tenía una incidencia cerrada.
TIEMPO_CIERRE_GUARDADO = "2 h 15 min"

# Tests de bugs de editar y dar seguimiento (incidencia-detalle.tsx y
# add-incidencia.tsx): incidencia guardada con su falla generada y datos de robo.
# La liga a la falla la arma helpers.incidencia_con_falla con el id, igual que
# el back (_url_registro_lkf).
FALLA_GENERADA_ID = "6a0000000000000000000009"
INCIDENCIA_CON_FALLA = {
    **INCIDENCIA_ANTES,
    "reporta_incidencia": GUARDIA_SESION,
    "fecha_hora_incidencia": "2026-11-13 10:00:00",
    "ubicacion_incidencia": LOCATION,
    "area_incidencia": AREA,
    "incidencia": "Choque",
    "categoria": "Incidentes de tránsito",
    "sub_categoria": "",
    "prioridad_incidencia": "Moderada",
    "comentario_incidencia": "Incidencia de prueba QA",
    "placas": "QA-INC-001",
    "marca": "Nissan",
    "seguimientos_incidencia": [],
    "tags": [],
}
# Lo que manda editarIncidencia del catálogo del tipo de incidencia.
EDICION_CATALOGO = {"categoria": "Incidentes de tránsito", "incidencia": "Choque", "incidente": "Choque", "sub_categoria": ""}
# Lo que manda editar desde el detalle: no trae la liga a la falla.
EDICION_SIN_LIGA = {"comentario_incidencia": "Se agregó la descripción del choque", "estatus": "cerrado"}

# Incidencia que el guardia captura como texto libre en el check de un rondín.
INCIDENCIA_DE_RONDIN = "Puerta del almacén abierta"
FOLIO_CHECK_RONDIN = "512-10"

# Incidencia guardada sin prioridad (registros viejos o creados desde un rondín).
INCIDENCIA_SIN_PRIORIDAD = {"folio": FOLIO_INCIDENCIA, "estatus": "abierto"}

# Cerrar una incidencia abierta: se creó hace 2 h 15 min (más unos segundos)
# y "Tiempo transcurrido al cierre" debe quedar con ese texto.
CREADA_HACE = {"hours": 2, "minutes": 15, "seconds": 30}
TIEMPO_CIERRE_CALCULADO = "2 horas, 15 minutos"
# Lo que manda el botón Cerrar incidencia del detalle (incidencia-detalle.tsx,
# datosCompletos + estatus "cerrado"): la incidencia completa, porque
# update_incidence reemplaza las respuestas del registro.
CERRAR_DESDE_DETALLE = {
    "reporta_incidencia": GUARDIA_SESION,
    "fecha_hora_incidencia": "2026-11-13 10:00:00",
    "ubicacion_incidencia": LOCATION,
    "area_incidencia": AREA,
    "incidencia": "Intrusión",
    "incidente": "Intrusión",
    "categoria": "Seguridad",
    "sub_categoria": "",
    "comentario_incidencia": "Incidencia de prueba QA",
    "dano_incidencia": "",
    "evidencia_incidencia": [],
    "documento_incidencia": [],
    "prioridad_incidencia": "Alta",
    "notificacion_incidencia": "no",
    "datos_deposito_incidencia": [],
    "tags": [],
    "estatus": "cerrado",
    "personas_involucradas_incidencia": [],
    "acciones_tomadas_incidencia": [],
    "seguimientos_incidencia": [],
    "afectacion_patrimonial_incidencia": [],
    "acciones_correctivas_incidencia": [],
}
