# coding: utf-8

"""
Datos de prueba para la sección Equipos (pestaña equipos de Bitácoras:
get_list_bitacora con desglose='equipos').
"""

from entradas_salidas.data.bitacora_data import (  # noqa: F401
    LOCATION,
    AREA,
    LIMITE_LISTA,
)

DESGLOSE_EQUIPOS = "equipos"

# Filtro de la opción "Dentro" (/bitacoras?tab=equipos&status=entrada).
FILTRO_DENTRO = [{"key": "status", "value": ["entrada"]}]

# Equipo con el que entra la visita. Serie única de esta suite para
# encontrarlo en la lista.
EQUIPO_VISITA = {
    "tipo": "Computo",
    "nombre": "Laptop prueba equipos",
    "marca": "Dell",
    "modelo": "Latitude",
    "color": "Negro",
    "serie": "QA-EQUIPOS-101",
}

# Visita con 2 equipos para recorrer Equipos de 1 fila por página (TB-103):
# los dos quedan en páginas distintas.
EQUIPOS_VISITA_DOS = [
    dict(EQUIPO_VISITA, serie="QA-EQUIPOS-103-A"),
    dict(EQUIPO_VISITA, tipo="Herramienta", nombre="Taladro prueba equipos", marca="Bosch",
         modelo="GSB", serie="QA-EQUIPOS-103-B"),
]
FILAS_POR_PAGINA = 1

# Equipo que el guardia agrega a una visita abierta desde el modal de agregar
# equipo (add-local-equipo.tsx): un objeto, sin 'action' (TB-104).
EQUIPO_AGREGADO = {
    "tipo": "Herramienta",
    "nombre": "Taladro agregado",
    "marca": "Bosch",
    "modelo": "GSB",
    "color": "Azul",
    "serie": "QA-EQUIPOS-104",
}
