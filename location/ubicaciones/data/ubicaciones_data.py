# coding: utf-8

"""
Datos de prueba para la sección Ubicaciones (+ Nueva Ubicación; script
location_sdk.py de Sanic).
"""

# Nombre que manda el front cuando el campo se deja en blanco.
NOMBRE_VACIO = "   "

# Ubicación de esta suite; en los tests de duplicado se simula que ya existe.
UBICACION_QA = "Planta QA Ubicaciones"
# Dirección que se captura en el modal cuando no se elige un contacto del
# catálogo (llaves de create_new_ubicacion).
DIRECCION_UBICACION = {
    "direccion": "Av. Constitución 100",
    "colonia": "Centro",
    "ciudad": "Monterrey",
    "estado": "Nuevo León",
    "codigo_postal": "64000",
    "pais": "México",
}
CREADO_OK = {"status_code": 201}
# Contacto que ya existe en el catálogo y se elige en el selector de
# dirección; trae su estatus y su _id, que no deben copiarse a la ubicación.
CONTACTO_QA = "Contacto QA Ubicaciones"
DIRECCION_CONTACTO = "Av. Fundidora 501"
CIUDAD_CONTACTO = "Monterrey"
ID_CONTACTO = "6a0000000000000000000351"
