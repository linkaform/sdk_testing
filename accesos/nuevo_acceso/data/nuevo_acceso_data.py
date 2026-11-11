# coding: utf-8

"""
Datos de prueba para la sección Nuevo Acceso (modal "Nueva Visita" de Accesos).

Usa la misma caseta que el resto de las pruebas de Accesos.
"""

import copy

from passes.integration.data.do_access_data import (  # noqa: F401
    LOCATION,
    AREA,
    FOTO_VALIDA,
    IDENTIFICACION_VALIDA,
    PASE_ACCESO_BASE,
    ACOMPANANTE_UNO,
    ACOMPANANTE_DOS,
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

# Pase de grupo (titular + 2 acompañantes) para la salida grupal en Accesos
# (TB-086). Se crea en + Nuevo Pase; en Accesos el guardia lo escanea y da
# ingreso y salida al grupo. Las fechas se llenan en el fixture.
PASE_GRUPO = copy.deepcopy(PASE_ACCESO_BASE)
PASE_GRUPO.update({
    "nombre": "Prueba salida grupal nuevo acceso",
    "email": "pruebas.nuevo_acceso@clave10.com",
    "acompanantes": 2,
    "acompanantes_grupo": [copy.deepcopy(ACOMPANANTE_UNO), copy.deepcopy(ACOMPANANTE_DOS)],
})

# Unitarios de do_access (sin red): el pase como lo regresa
# get_detail_access_pass, activo, para la ubicación de la caseta, sin días
# limitados ni límite de entradas. Cada test cambia solo lo que revisa.
QR_PASE_UNIT = "6650a1b2c3d4e5f6a7b8c9d1"
PASE_DETALLE_ACTIVO = {
    "_id": QR_PASE_UNIT,
    "estatus": "activo",
    "ubicacion": [LOCATION],
    "limitado_a_dias": [],
    "limite_de_acceso": 0,
    "tipo_visita_pase": "rango_de_fechas",
    "fecha_de_expedicion": "",
    "fecha_de_caducidad": "",
}
# get_count_ingresos sin entradas registradas.
SIN_INGRESOS = {}
# do_access decide el día de hoy con esta lista y en la zona de CDMX.
DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
ZONA_DIA_ACCESO = "America/Mexico_City"
# Pase con límite de 3 entradas que ya las usó (get_count_ingresos).
LIMITE_ENTRADAS = 3
INGRESOS_EN_EL_LIMITE = {"total_records": LIMITE_ENTRADAS}
# Fechas del pase relativas a ahora, en minutos (do_access da 1 hora de
# margen después de la caducidad).
VENCIDO_HACE_MIN = 120
DENTRO_DE_TOLERANCIA_MIN = 30
# Respuesta del registro de la entrada en la bitácora cuando se guarda bien.
ENTRADA_REGISTRADA = {"status_code": 201, "json": {"id": "6650a1b2c3d4e5f6a7b8c9d2"}}
# Pase de fecha fija: la cita con 60 min de diferencia contra ahora queda
# fuera de la tolerancia por defecto (15 min antes o después, sin requisitos
# de la ubicación en la configuración). Vigente 2 horas más.
CITA_FUERA_DE_TOLERANCIA_MIN = 60
VIGENTE_POR_MIN = 120
CONFIG_SIN_TOLERANCIA = {"requisitos": []}
# Ubicación de otro pase (no la de la caseta); también se usa en otros tests.
OTRA_UBICACION = "Planta Durango"

# Nueva Visita en modo "Fecha Fija": el front deriva fecha_desde_visita como
# el día anterior a la fecha elegida (getPreviousDay) y limita el acceso al
# día de la semana de esa fecha (aplicarDiaDeAccesoFijo). Las fechas y el día
# se llenan en el fixture.
PASE_NUEVA_VISITA_FECHA_FIJA = copy.deepcopy(PASE_NUEVA_VISITA)
PASE_NUEVA_VISITA_FECHA_FIJA.update({
    "nombre": "Prueba nueva visita fecha fija",
    "tipo_visita_pase": "fecha_fija",
    "config_dia_de_acceso": "limitar_días_de_acceso",
})
