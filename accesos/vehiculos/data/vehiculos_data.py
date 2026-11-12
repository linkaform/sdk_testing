# coding: utf-8

"""
Datos de prueba para la sección Vehículos (pestaña vehiculos de Bitácoras:
get_list_bitacora con desglose='vehiculos').
"""

from entradas_salidas.data.bitacora_data import (  # noqa: F401
    LOCATION,
    AREA,
    LIMITE_LISTA,
)

DESGLOSE_VEHICULOS = "vehiculos"

# Filtro de la opción "Dentro" (/bitacoras?tab=vehiculos&status=entrada).
FILTRO_DENTRO = [{"key": "status", "value": ["entrada"]}]

# Vehículo con el que entra la visita. Placas únicas de esta suite para
# encontrarlo en la lista.
VEHICULO_VISITA = {
    "tipo": "Automóvil",
    "marca": "Nissan",
    "modelo": "Versa",
    "estado": "Nuevo León",
    "placas": "QA-VEHICULOS-095",
    "color": "Blanco",
}

# Visita con 2 vehículos para recorrer Vehículos de 1 fila por página (TB-097):
# los dos quedan en páginas distintas.
VEHICULOS_VISITA_DOS = [
    dict(VEHICULO_VISITA, placas="QA-VEHICULOS-097-A"),
    dict(VEHICULO_VISITA, marca="Toyota", modelo="Hilux", placas="QA-VEHICULOS-097-B"),
]
FILAS_POR_PAGINA = 1

# Vehículo que el guardia agrega a una visita abierta desde el modal
# "Nuevo Vehículo" (add-local-vehicule.tsx): un objeto, sin 'action' (TB-098).
VEHICULO_AGREGADO = {
    "color": "Rojo",
    "marca": "Ford",
    "modelo": "Ranger",
    "estado": "Nuevo León",
    "placas": "QA-VEHICULOS-098",
    "tipo": "Automóvil",
    "foto_vehiculo": [],
}

# Visita con un vehículo con tipo y otro sin tipo (renglón vacío del grupo):
# la lista Dentro omite el que no tiene tipo; el contador de vehículos dentro
# debe contar lo mismo (TB-099, ticket 2610-1484).
VEHICULOS_CON_Y_SIN_TIPO = [
    dict(VEHICULO_VISITA, placas="QA-VEHICULOS-099"),
    dict(VEHICULO_VISITA, tipo="", placas="QA-VEHICULOS-099-SIN-TIPO"),
]

# La app pide Vehículos Dentro con list_bitacora2 sin desglose y con la
# prioridad 'entrada'; desglosa los vehículos en el celular (TB-100).
PRIORIDADES_APP_DENTRO = ["entrada"]
VEHICULO_APP = dict(VEHICULO_VISITA, placas="QA-VEHICULOS-100")

# Unitarios (vehiculos/unit). El mismo vehículo con las llaves largas que
# también acepta el pase, y con las etiquetas de la lista (format_cr). El
# renglón vacío es el que dejan los grupos repetitivos sin llenar.
VEHICULO_LLAVES_LARGAS = {
    "tipo_vehiculo": VEHICULO_VISITA["tipo"],
    "marca_vehiculo": VEHICULO_VISITA["marca"],
    "modelo_vehiculo": VEHICULO_VISITA["modelo"],
    "nombre_estado": VEHICULO_VISITA["estado"],
    "placas_vehiculo": VEHICULO_VISITA["placas"],
    "color_vehiculo": VEHICULO_VISITA["color"],
}
RENGLON_VACIO = {}
