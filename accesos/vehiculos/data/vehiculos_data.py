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
