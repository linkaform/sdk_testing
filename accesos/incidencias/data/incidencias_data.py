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
