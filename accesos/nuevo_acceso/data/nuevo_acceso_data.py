# coding: utf-8

"""
Datos de prueba para la sección Nuevo Acceso (modal "Nueva Visita" de Accesos).

Usa la misma caseta que el resto de las pruebas de Accesos.
"""

from passes.integration.data.do_access_data import (  # noqa: F401
    LOCATION,
    AREA,
    FOTO_VALIDA,
    IDENTIFICACION_VALIDA,
)

# Llaves que regresa assets_access_pass y que el modal Nueva Visita usa para
# llenar áreas, anfitriones (Visita_a), perfiles y requerimientos.
LLAVES_ASSETS = {"Areas", "Visita_a", "Perfiles", "requerimientos", "envios"}

# assets_access_pass con la configuración de la ubicación fallando (TB-079):
# áreas y anfitriones simulados que sí se obtienen.
AREAS_SIMULADAS = [AREA]
ANFITRIONES_SIMULADOS = [{"name": "Anfitrión prueba nueva visita"}]

# Pase con el mismo payload que arma el front al guardar en Nueva Visita
# (add-visit-modal.tsx + access.ts::addNewVisit). visita_a va como texto y
# las fechas se llenan en el fixture con el día de hoy.
PASE_NUEVA_VISITA = {
    "site": "accesos",
    "nombre": "Prueba nueva visita",
    "empresa": "Clave10",
    "visita_a": "",
    "perfil_pase": "Visita general",
    "foto": FOTO_VALIDA,
    "identificacion": IDENTIFICACION_VALIDA,
    "email": "",
    "telefono": "",
    "created_from": "nueva_visita",
    "ubicaciones": [LOCATION],
    "tipo_visita_pase": "rango_de_fechas",
    "fechaFija": "",
    "fecha_desde_visita": "",
    "fecha_desde_hasta": "",
    "config_dia_de_acceso": "cualquier_día",
    "config_dias_acceso": [],
    "config_limitar_acceso": 0,
}

# QR que no es un ObjectId (lo que pasa si se escribe texto en el buscador).
QR_INVALIDO = "no-es-un-qr"

# Vehículo, equipo y comentario que el guardia agrega en + Nuevo Acceso antes
# de Registrar Ingreso (mismas llaves que manda el front en do_access).
# Placas y serie únicas de esta suite para encontrarlos en la visita.
VEHICULO_NUEVA_VISITA = {
    "tipo": "Automóvil",
    "marca": "Nissan",
    "modelo": "Versa",
    "estado": "Nuevo León",
    "placas": "QA-NUEVO-ACCESO-084",
    "color": "Blanco",
}
EQUIPO_NUEVA_VISITA = {
    "tipo": "computo",
    "nombre": "Laptop prueba nuevo acceso",
    "marca": "Dell",
    "modelo": "Latitude",
    "color": "Negro",
    "serie": "QA-NUEVO-ACCESO-084",
}
COMENTARIO_PASE_NUEVA_VISITA = {
    "comentario_pase": "Comentario de prueba nuevo acceso",
    "tipo_de_comentario": "pase",
}

# Límite de entradas para probar un segundo ingreso (TB-085): do_access revisa
# el límite antes que si la persona ya está dentro, y sin límite explícito el
# pase queda con 1 entrada (app.py:3181).
LIMITE_VARIAS_ENTRADAS = 5
