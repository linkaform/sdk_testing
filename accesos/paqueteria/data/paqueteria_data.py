# coding: utf-8

"""
Datos de prueba para la sección Paquetería de Activos (+ Nuevo Paquete,
Pendientes, Entregados y Todos; script paqueteria.py).
"""

from pases_entrada.data.datos_base import (  # noqa: F401
    LOCATION,
    AREA,
    FOTO_VALIDA,
)

# Paquete con el payload que arma el modal + Nuevo Paquete (add-paqueteria.tsx
# → paqueteria.ts crearPaqueteria) para un destinatario empleado. Proveedor y
# locker se toman en el fixture de un paquete que ya existe en la ubicación
# (valores reales de sus catálogos); el destinatario es el empleado del
# usuario. La descripción lleva un sufijo único por corrida y la fecha de
# recibido se llena en el fixture. Se crea sin notificación para no mandar
# correos ni SMS reales.
PAQUETE_NUEVO = {
    "ubicacion_paqueteria": LOCATION,
    "area_paqueteria": AREA,
    "fotografia_paqueteria": FOTO_VALIDA,
    "descripcion_paqueteria": "",
    "quien_recibe_paqueteria": "",
    "guardado_en_paqueteria": "",
    "fecha_recibido_paqueteria": "",
    "fecha_entregado_paqueteria": "",
    "entregado_a_paqueteria": "",
    "estatus_paqueteria": ["guardado"],
    "proveedor": "",
}
DESCRIPCION_PAQUETE = "Paquete de prueba QA"

# Destinatario externo ("Otro"): el front manda quien_recibe_otro en lugar de
# quien_recibe_paqueteria.
DESTINATARIO_EXTERNO = "Destinatario externo QA"

# Las descripciones editadas también llevan un sufijo único por corrida.
DESCRIPCION_EDITADA = "Paquete de prueba QA editado"

# Lo que manda entregar-paqueteria.tsx al entregar el paquete; la fecha de
# entrega se llena en el helper.
ENTREGADO_A = "Persona que recoge QA"

# Estatus de la lista (menú de Paquetería): Pendientes = guardado,
# Entregados = entregado, Todos = sin filtro.
ESTATUS_GUARDADO = "guardado"
ESTATUS_ENTREGADO = "entregado"
ESTATUS_TODOS = ""

# La lista del front pagina y filtra con el buscador (facets); la descripción
# escrita va con exact False ("contiene").
FACET_DESCRIPCION = "descripcion_paqueteria"
LIMITE_LISTA = 50

# Unitarios (paqueteria/unit): el paquete como lo manda + Nuevo Paquete con
# todo lleno, para un empleado o para "Otro". METADATA_PAQUETE es lo que
# regresa get_metadata (la forma no importa: se revisan los answers).
OTRA_UBICACION = "Planta Durango"
PAQUETE_UNIT = {
    **PAQUETE_NUEVO,
    "descripcion_paqueteria": DESCRIPCION_PAQUETE,
    "quien_recibe_paqueteria": "Empleado de prueba QA",
    "guardado_en_paqueteria": "Locker de prueba QA",
    "proveedor": "Proveedor de prueba QA",
    "fecha_recibido_paqueteria": "2026-11-12 10:00:00",
}
PAQUETE_UNIT_OTRO = {
    key: value for key, value in PAQUETE_UNIT.items() if key != "quien_recibe_paqueteria"
}
PAQUETE_UNIT_OTRO["quien_recibe_otro"] = DESTINATARIO_EXTERNO
METADATA_PAQUETE = {}
GUARDADO_OK = {"status_code": 201}
GUARDADO_FALLIDO = {"status_code": 400}
# Aviso al destinatario: canales como los manda el front, con y sin email.
CANALES_CORREO = ["correo"]
AVISO_CORREO = {"canales": CANALES_CORREO, "email": "destinatario.qa@clave10.com"}
AVISO_SIN_EMAIL = {"canales": CANALES_CORREO, "email": ""}
AVISO_ENVIADO = {"correo": {"ok": True, "error": None}}

# Editar y entregar (update_paquete): folio del paquete y lo que mandan
# entregar-paqueteria.tsx (estatus en lista) y editar-paqueteria.tsx (los
# campos del paquete, sin estatus).
FOLIO_PAQUETE = "1-PAQUETE"
EDICION_OK = {"status_code": 202}
ENTREGA_PAQUETE = {
    "estatus_paqueteria": [ESTATUS_ENTREGADO],
    "fecha_entregado_paqueteria": "2026-11-17 12:00:00",
    "entregado_a_paqueteria": ENTREGADO_A,
}
EDICION_PAQUETE = {
    key: PAQUETE_UNIT[key]
    for key in (
        "ubicacion_paqueteria", "area_paqueteria", "fotografia_paqueteria", "descripcion_paqueteria",
        "quien_recibe_paqueteria", "guardado_en_paqueteria", "fecha_recibido_paqueteria",
        "entregado_a_paqueteria", "proveedor",
    )
}

# Lista de paquetes (get_paquetes): un paquete de destinatario externo como
# lo regresa la consulta, con el estatus en lista.
PAQUETE_LISTA_OTRO = {
    "folio": FOLIO_PAQUETE,
    "quien_recibe_otro": DESTINATARIO_EXTERNO,
    "estatus_paqueteria": [ESTATUS_GUARDADO],
}
# Aviso por correo con número de guía, y respuesta del envío.
NO_GUIA = "GUIA-QA-123"
AVISO_CORREO_GUIA = {**AVISO_CORREO, "no_guia": NO_GUIA}
CORREO_ENVIADO = {"status_code": 200}
# Aviso por SMS con un teléfono incompleto (menos de 10 dígitos).
AVISO_SMS_TELEFONO_CORTO = {"canales": ["sms"], "telefono": "81 1234"}
# Empleados para el catálogo de destinatarios: uno con usuario ligado y
# contacto en la forma Empleados, y uno sin nombre (se omite).
EMPLEADO_CON_USUARIO = {
    "worker_name": "Empleado de prueba QA",
    "usuario_email": ["usuario.qa@clave10.com"],
    "correo_empresarial": "empleado.qa@clave10.com",
    "usuario_telefono": [],
    "telefono1": "8110000001",
}
EMPLEADO_SIN_NOMBRE = {"worker_name": "", "usuario_email": ["sin.nombre@clave10.com"]}
