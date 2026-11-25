# coding: utf-8

"""
Datos de prueba para la sección Contratistas (back de Sanic:
lkf-sanic-apps/addons/accesos/contratistas_*.py, scripts *_sdk.py de
sdk-modules-sanic). Ids inventados: los tests no tocan la cuenta.
"""

from datetime import date

# "Hoy" fijo para que vigencias y periodos no dependan de la fecha de la corrida.
HOY = date(2026, 6, 15)

# Empresas (registros de la forma Empresas).
CLIENTE = "6900000000000000000000c1"
OTRO_CLIENTE = "6900000000000000000000c2"
CONTRATISTA = "6900000000000000000000a1"
SUBCONTRATISTA = "6900000000000000000000b1"

REQUERIMIENTO_ID = "6900000000000000000000f1"
RELACION_PADRE_ID = "6900000000000000000000e1"

# Requerimientos normalizados como los deja _cum_requerimiento.
REQ_BIMESTRAL_ICSOE = {
    "vigencia_modo": "Periodo",
    "periodicidad": "Bimestral",
    "meses_periodo": [1, 5, 9],  # ICSOE: se entrega en enero, mayo y septiembre
    "dia_limite": 0,             # sin día: el default de la spec (17)
}
REQ_MENSUAL = {"vigencia_modo": "Periodo", "periodicidad": "Mensual", "meses_periodo": [], "dia_limite": 10}
REQ_VIGENCIA = {"vigencia_modo": "Vigencia", "periodicidad": "Única", "meses_periodo": [], "dia_limite": 0}

# Registro público (RG-01): persona moral válida.
REGISTRO_MORAL = {
    "perfil": "Contratista",
    "tipo_persona": "moral",
    "razon_social": "  Limpieza   Industrial del Norte  ",
    "rfc": "lin 010203 ab1",
    "representante_legal": "Ana Pérez",
    "email": " Contacto@Limpieza.MX ",
    "telefono": "+52 (81) 1234-5678",
    "direccion": "Av. Siempre Viva 742, Monterrey",
    "dominio": "Limpieza Industrial Ñorte",
    "password": "Segura#2026",
    "password2": "Segura#2026",
    "terminos": True,
}

# Catálogo maestro de requerimientos (ME-13) como lo arma _map_catalogo.
CATALOGO_MAESTRO = [
    {"id": "r1", "nombre": "Constancia de situación fiscal", "codigo": "CSF", "nivel": "Empresa"},
    {"id": "r2", "nombre": "Constancia de habilidades DC-3", "codigo": "DC3", "nivel": "Persona"},
    {"id": "r3", "nombre": "Opinión de cumplimiento IMSS", "codigo": "OPINION-IMSS", "nivel": "Empresa"},
]
