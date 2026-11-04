# coding: utf-8

"""
Datos de prueba para la sección Pases de Entrada (+ Nuevo Pase y las
pestañas Activos, Por autorizar, En Proceso y Todos de la lista de pases).
"""

import copy

from passes.integration.data.do_access_data import (  # noqa: F401
    LOCATION,
    PASE_ACCESO_BASE,
)

# Pase con el payload que arma el front al guardar + Nuevo Pase
# (pase-entrada/page.tsx → add-pass-modal.tsx). Las fechas se llenan en el
# fixture. auto_activacion "no" = el guardia apagó "Activar pase por defecto";
# sin habilitar_fotografia/identificacion = la ubicación no pide foto ni
# identificación (el front no manda esas llaves).
PASE_NUEVO = copy.deepcopy(PASE_ACCESO_BASE)
PASE_NUEVO.update({
    "nombre": "Prueba pases de entrada",
    "email": "pruebas.pases_entrada@clave10.com",
    "descripcion": "test pases_entrada",
    "comentarios": [],
    "enviar_correo_pre_registro": [],
    "auto_activacion": "no",
    "acompanantes": 0,
    "acompanantes_grupo": [],
})

# Pestañas de la lista de pases (tab_status de get_my_pases, pases/page.tsx).
TAB_EN_PROCESO = "en_proceso"
TAB_ACTIVOS = "activos"
ESTATUS_PROCESO = "proceso"

# Registros por página al consultar la lista de pases filtrada por nombre.
LIMITE_LISTA = 50
