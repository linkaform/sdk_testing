# coding: utf-8

"""
Datos de prueba para la sección Paquetería de Activos (+ Nuevo Paquete,
Pendientes, Entregados y Todos; script paqueteria.py).
"""

from passes.integration.data.do_access_data import (  # noqa: F401
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

# Estatus de la lista (menú de Paquetería): Pendientes = guardado.
ESTATUS_GUARDADO = "guardado"

# La lista del front pagina y filtra con el buscador (facets); la descripción
# escrita va con exact False ("contiene").
FACET_DESCRIPCION = "descripcion_paqueteria"
LIMITE_LISTA = 50
