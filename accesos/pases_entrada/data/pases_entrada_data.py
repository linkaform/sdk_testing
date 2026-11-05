# coding: utf-8

"""
Datos de prueba para la sección Pases de Entrada (+ Nuevo Pase y las
pestañas Activos, Por autorizar, En Proceso y Todos de la lista de pases).
"""

import copy

from passes.integration.data.do_access_data import (  # noqa: F401
    LOCATION,
    PASE_ACCESO_BASE,
    FOTO_VALIDA,
    IDENTIFICACION_VALIDA,
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
TAB_POR_AUTORIZAR = "por_autorizar"
TAB_TODOS = ""
ESTATUS_PROCESO = "proceso"
ESTATUS_ACTIVO = "activo"
ESTATUS_POR_AUTORIZAR = "por_autorizar"

# Registros por página al consultar la lista de pases filtrada por nombre.
LIMITE_LISTA = 50

# Lo que manda el visitante al completar su pase: lo arma el modal de
# confirmación de pase-update (add-pass-modal-2.tsx → update_pass), que pasa
# los avisos a "sí"/"no". El formulario obliga a aceptar el de privacidad; los
# de datos personales y reglas de acceso no se llenan en esa pantalla. nombre,
# email y teléfono se llenan en el test con los del pase.
PASE_COMPLETAR = {
    "grupo_vehiculos": [],
    "grupo_equipos": [],
    "equipo_vehiculo_acompanante": [],
    "status_pase": "Activo",
    "walkin_fotografia": FOTO_VALIDA,
    "walkin_identificacion": IDENTIFICACION_VALIDA,
    "acepto_aviso_privacidad": "sí",
    "acepto_aviso_datos_personales": "no",
    "acepto_reglas_acceso": "no",
    "conservar_datos_por": "3 meses",
    "acompanantes": 0,
    "grupo_acompanantes": [],
}

# Pase de auto registro: el visitante se registra solo desde el link público
# (registro-ingreso → add-pass-create-modal.tsx → create_access_pass). Trae
# foto e identificación, pero el backend no lo auto-autoriza, así que queda
# completo y sin autorizar. Sin fechas (el backend usa hoy). visita_a se llena
# en el fixture con el email del usuario de la cuenta (el anfitrión). En auto
# registro el teléfono va con 10 dígitos, sin lada internacional.
PASE_AUTO_REGISTRO = {
    "ubicaciones": [LOCATION],
    "nombre": "Prueba auto registro pases",
    "perfil_pase": "Walkin",
    "telefono": "8110000099",
    "visita_a": {},
    "email": "pruebas.auto_registro@clave10.com",
    "empresa": "Clave10",
    "foto": FOTO_VALIDA,
    "identificacion": IDENTIFICACION_VALIDA,
    "equipos": [],
    "vehiculos": [],
    "motivo": "Prueba pases de entrada",
    "created_from": "auto_registro",
    "acepto_aviso_privacidad": "true",
    "conservar_datos_por": "3 meses",
    "firma_reglas_de_acceso": {"file_url": "", "file_name": ""},
    "acepto_reglas_ingreso": "false",
}
