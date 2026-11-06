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

# + Nuevo Pase con los toggles del formulario (pase-entrada/page.tsx). El front
# manda auto_activacion solo si la ubicación permite "Activar pase por
# defecto", y habilitar_fotografia/identificacion ("sí"/"no", con acento) solo
# si la ubicación pide ese dato; el admin puede apagarlos. Sin foto ni
# identificación: el front solo las captura con la auto activación prendida.
PASE_AUTO_ACTIVACION = copy.deepcopy(PASE_NUEVO)
PASE_AUTO_ACTIVACION.update({
    "auto_activacion": "sí",
    "habilitar_fotografia": "sí",
    "habilitar_identificacion": "sí",
})

PASE_SIN_REQUISITOS = copy.deepcopy(PASE_NUEVO)
PASE_SIN_REQUISITOS.update({
    "habilitar_fotografia": "no",
    "habilitar_identificacion": "no",
})

PASE_PIDE_FOTO_E_IDENTIFICACION = copy.deepcopy(PASE_NUEVO)
PASE_PIDE_FOTO_E_IDENTIFICACION.update({
    "habilitar_fotografia": "sí",
    "habilitar_identificacion": "sí",
})

# Configuración de la ubicación que pide + Nuevo Pase al elegir la ubicación
# (useGetConfSeguridad → get_config_modulo_seguridad).
LLAVES_CONFIG_UBICACION = {
    "ubicaciones",
    "ubicaciones_info",
    "requerimientos",
    "envios",
    "tipos",
    "condiciones_servicio",
    "permisos_certificaciones",
    "logotipo_pase",
    "auto_activacion",
    "acompanantes_requeridos",
    "empresa",
}
LLAVES_LISTA_CONFIG = ("requerimientos", "envios", "tipos")
REQUERIMIENTOS_VALIDOS = {"fotografia", "identificacion"}
VALORES_SI_NO = {"sí", "no"}

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

# Paginación y buscador de la lista de pases (pases/page.tsx → useFacetSection).
# El buscador manda los filtros como facets {key, values, exact}; un texto
# escrito va con exact False ("contiene"). Los pases de estas pruebas llevan un
# sufijo único por corrida para que la lista solo traiga los suyos.
FACET_NOMBRE = "nombre"
PASES_PARA_PAGINAR = 3
LIMITE_PAGINA = 2
PAGINAS_ESPERADAS = 2

# Lo que manda el botón "Cancelar pase" de view-pass-modal (update_pass).
CANCELAR_PASE = {"status_pase": "cancelado"}
ESTATUS_CANCELADO = "cancelado"
