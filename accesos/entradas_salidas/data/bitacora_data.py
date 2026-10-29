# coding: utf-8

"""
Datos de prueba para la sección Entradas & Salidas (bitácora de accesos).

Reutiliza el pase base de do_access (mismo shape que manda el front al crear
un pase) y solo cambia nombre/email para que los registros de esta suite se
distingan en la bitácora de preprod.
"""

import copy
from datetime import timedelta

from passes.integration.data.do_access_data import (
    PASE_ACCESO_BASE,
    LOCATION,
    AREA,
)

PASE_BITACORA = copy.deepcopy(PASE_ACCESO_BASE)
PASE_BITACORA.update({
    "nombre": "Prueba bitacora entradas salidas",
    "email": "pruebas.bitacora@clave10.com",
    "descripcion": "test entradas_salidas",
    "comentarios": [
        {"tipo_comentario": "pase", "comentario_pase": "pase de prueba entradas_salidas"}
    ],
})

# Otra ubicación real de la cuenta, con una caseta suya. Sirve para tener
# una visita abierta fuera de LOCATION (salida masiva por ubicación, TB-070).
OTRA_LOCATION = "Planta Durango"
OTRA_AREA = "Caseta Principal -Dro"

PASE_BITACORA_OTRA_UBICACION = copy.deepcopy(PASE_BITACORA)
PASE_BITACORA_OTRA_UBICACION.update({
    "nombre": "Prueba bitacora otra ubicacion",
    "ubicaciones": [OTRA_LOCATION],
})

# Ubicación que no existe en el pase ni en la cuenta: sirve para probar la
# salida por una caseta distinta a la de entrada.
UBICACION_INEXISTENTE = "Ubicacion Que No Existe En El Pase"

# record_id con formato inválido para Mongo (no es un ObjectId de 24 hex).
RECORD_ID_INVALIDO = "no-es-un-object-id"

# Equipo para editar un registro de bitácora (update_bitacora_entrada).
EQUIPO_PRUEBA = {
    "tipo": "computo",
    "nombre": "Laptop prueba bitacora",
    "marca": "Dell",
    "modelo": "Latitude",
    "color": "Negro",
    "serie": "QA-BITACORA-001",
}

# Documento que deja el visitante a cambio del gafete (mismo valor que el
# radio "INE" del modal de gafete en el front).
DOCUMENTO_GAFETE = "ine"

# Formato legible de la duración que guarda do_out: sin segundos y solo las
# partes que no son cero ("Menos de 1 min", "25 min", "3 h 25 min",
# "1 día 1 h 5 min", "2 días 2 h").
DURACION_REGEX = r"^(?:Menos de 1 min|(?:\d+ días? )?(?:\d+ h )?\d+ min|\d+ días?(?: \d+ h)?|\d+ h)$"

# Registros por página al consultar la lista de bitácora. La lista se ordena
# por created_at descendente, así que la visita recién creada sale en la
# primera página.
LIMITE_LISTA = 50

# Dos vehículos para registrar una entrada con varios vehículos (desglose de la
# lista). Placas únicas de esta suite.
VEHICULOS_DESGLOSE = [
    {"tipo": "Automóvil", "marca": "Nissan", "modelo": "Versa", "estado": "Nuevo León",
     "placas": "QA-DESGLOSE-01", "color": "Blanco"},
    {"tipo": "Camioneta", "marca": "Ford", "modelo": "Ranger", "estado": "Nuevo León",
     "placas": "QA-DESGLOSE-02", "color": "Gris"},
]

# Facets del buscador de la bitácora (TB-053). El nombre va con otra
# combinación de mayúsculas y acentos que PASE_BITACORA["nombre"] para probar
# la búsqueda "contiene"; nombre_y_salida combina dos facets (AND) que la
# visita abierta no cumple porque sigue en entrada.
FACETS_BUSQUEDA = {
    "por_nombre": [
        {"key": "nombre_visitante", "values": ["PRUEBA BITÁCORA ENTRADAS"], "exact": False},
    ],
    "nombre_y_salida": [
        {"key": "nombre_visitante", "values": ["prueba bitacora entradas"], "exact": False},
        {"key": "status", "values": ["salida"], "exact": True},
    ],
}

# Vehículo para agregar a una entrada (update_bitacora_entrada). Las placas
# son únicas de esta suite para encontrarlo sin ambigüedad en la visita.
VEHICULO_PRUEBA = {
    "tipo": "Automóvil",
    "marca": "Nissan",
    "modelo": "Versa",
    "estado": "Nuevo León",
    "placas": "QA-BITACORA-064",
    "color": "Blanco",
}

# Mismo equipo con otros datos, para editarlo (update_bitacora_entrada, action
# 'edit'). Serie distinta para comprobar que se reemplazó y no se duplicó.
EQUIPO_EDITADO = dict(EQUIPO_PRUEBA, nombre="Laptop prueba bitacora editada", serie="QA-BITACORA-066")

# Visitas abiertas que regresa la consulta de la salida masiva en el test
# unitario (TB-072). Son de ubicaciones distintas: sin ubicación, la salida
# masiva no debería cerrarlas.
VISITAS_ABIERTAS_OTRAS_UBICACIONES = [
    {"_id": "6ae000000000000000000001"},
    {"_id": "6ae000000000000000000002"},
]

# Mensaje de force_quit_all_persons cuando no hay nadie dentro (TB-071).
MSG_SIN_PERSONAS_DENTRO = "No hay personas dentro por registrar salida."

# Duración de la salida (do_out) en los tests unitarios (TB-063, TB-076).
# Visita abierta simulada; checkin_date se arma en el test con la hora actual.
VISITA_ABIERTA_DURACION = {
    "folio": "QA-DURACION-10",
    "status_visita": "entrada",
    "ubicacion_entrada": LOCATION,
}
# Margen entre la hora guardada en la salida y la hora del empleado.
MARGEN_HORA_SALIDA = timedelta(minutes=2)

# Empleado en una zona con otra hora que CDMX (Cancún va 1 h adelante).
ZONA_EMPLEADO_OTRA = "America/Cancun"
ENTRADA_HACE_10_MIN = timedelta(minutes=10, seconds=30)
DURACION_10_MIN = "10 min"

# Visita de más de 24 h, con empleado en CDMX para no mezclar zonas.
ZONA_EMPLEADO_CDMX = "America/Mexico_City"
ENTRADA_HACE_MAS_DE_UN_DIA = timedelta(days=1, hours=1, minutes=5, seconds=30)
DURACION_MAS_DE_UN_DIA = "1 día 1 h 5 min"

# Cierre general (salida masiva, force_quit_all_persons) en el test unitario
# TB-077: visitas abiertas de LOCATION y el texto que va en la duración,
# porque no se sabe la hora real en que salió cada persona.
VISITAS_ABIERTAS_UBICACION = [
    {"_id": "6ae000000000000000000011"},
    {"_id": "6ae000000000000000000012"},
]
DURACION_CIERRE_GENERAL = "Cierre general"
