# coding: utf-8

"""
Datos de prueba para la sección Entradas & Salidas (bitácora de accesos).

Reutiliza el pase base de do_access (mismo shape que manda el front al crear
un pase) y solo cambia nombre/email para que los registros de esta suite se
distingan en la bitácora de preprod.
"""

import copy

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

# Formato de la duración que guarda do_out.
DURACION_REGEX = r"^\d{2}:\d{2}:\d{2}$"

# Registros por página al consultar la lista de bitácora. La lista se ordena
# por created_at descendente, así que la visita recién creada sale en la
# primera página.
LIMITE_LISTA = 50

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
