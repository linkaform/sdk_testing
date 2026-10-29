# coding: utf-8

"""
Datos de prueba para la sección Nuevo Acceso (modal "Nueva Visita" de Accesos).

Usa la misma caseta que el resto de las pruebas de Accesos.
"""

from passes.integration.data.do_access_data import (  # noqa: F401
    LOCATION,
    AREA,
)

# Llaves que regresa assets_access_pass y que el modal Nueva Visita usa para
# llenar áreas, anfitriones (Visita_a), perfiles y requerimientos.
LLAVES_ASSETS = {"Areas", "Visita_a", "Perfiles", "requerimientos", "envios"}

# assets_access_pass con la configuración de la ubicación fallando (TB-079):
# áreas y anfitriones simulados que sí se obtienen.
AREAS_SIMULADAS = [AREA]
ANFITRIONES_SIMULADOS = [{"name": "Anfitrión prueba nueva visita"}]
