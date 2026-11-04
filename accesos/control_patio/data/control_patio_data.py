# coding: utf-8

"""
Datos de prueba para la sección Transportistas – Control de patio
(bitácora de transportistas, script transportistas.py).
"""

from passes.integration.data.do_access_data import (  # noqa: F401
    LOCATION,
    AREA,
)

# Llegada de un camión sin pase, con el payload que arma el front en
# "Nuevo Acceso Transportista" (nuevo-acceso-transportista-modal.tsx).
# Placas únicas de esta suite para encontrarlo en el patio.
LLEGADA_SIN_PASE = {
    "creado_desde": "acceso_web",
    "tipo_operacion": "Entrega",
    "ubicacion": LOCATION,
    "area": AREA,
    "vehiculo": {
        "transportista": "Transportes prueba QA",
        "procedencia": "Monterrey",
        "tipo_vehiculo": "Tractocamión",
        "placa": "QA-PATIO-087",
        "no_economico": "QA-087",
        "marca": "Kenworth",
        "modelo": "2020",
        "color": "Blanco",
        "placa_tarjeta_circulacion": None,
    },
    "conductor": {
        "nombre": "Conductor prueba patio",
        "celular": None,
        "no_licencia": None,
        "vigencia_licencia": None,
        "rfc": None,
        "acompanante": None,
    },
    "embarque": {
        "proveedor_cliente": None,
        "no_orden_compra": None,
    },
    "documentos_adicionales": [],
    "remolques": [],
    "contenedores": [],
    "materiales": [],
}

# Estatus en que queda el camión al registrar su llegada y al descartarlo.
ESTATUS_ARRIBO = "arribo"
ESTATUS_DESCARTADO = "descartado"

# Pase de transportista con el payload que arma el front en "+ Nuevo Pase
# Transportistas" (pase-entrada-transportista/page.tsx::buildPayload). Al
# crearse deja un registro 'programado' en el patio. Fecha y andén se llenan
# en el fixture (hoy y el primer andén de la cuenta).
PASE_TRANSPORTISTA = {
    "tipo_de_operacion": "entrega_de_materia_prima",
    "creado_desde": "pase_de_entrada_web",
    "dominio": "",
    "crea_el_pase": {
        "nombre": "Prueba control de patio",
        "email": "pruebas.control_patio@clave10.com",
        "telefono": None,
        "es_nuevo": False,
    },
    "empresa_transportista": "Transportes prueba QA",
    "recibe_el_pase": {"nombre": None, "email": None, "telefono": None},
    "material": {
        "proveedor_cliente": None,
        "orden_compra": None,
        "items": [],
        "documentos": [],
    },
    "lugar_entrega_recepcion": {
        "ubicacion": LOCATION,
        "direccion": None,
        "fecha_pase_transportista_desde": "",
        "horario_disponible": None,
        "anden": "",
        "area": AREA,
    },
}
ESTATUS_PROGRAMADO = "programado"
PASE_COMPLETADO = "completado"

# Etapas del patio después de 'arribo', en el orden del botón "avanzar etapa"
# del detalle (ORDEN_ESTATUS en accesos/transportista/[id]/page.tsx).
ESTATUS_CARGA_DESCARGA = "carga_/_descarga"
ESTATUS_TERMINADO = "terminado"
ETAPAS_HASTA_TERMINADO = ["inspeccion_entrada", ESTATUS_CARGA_DESCARGA, "inspeccion_salida", ESTATUS_TERMINADO]

# Columnas de etapas del Kanban del patio (COLUMNAS en
# bitacoras_transportistas/page.tsx). Un camión descartado ya no sale en ellas.
ESTATUS_COLUMNAS_KANBAN = ["arribo", "inspeccion_entrada", ESTATUS_CARGA_DESCARGA, "inspeccion_salida", ESTATUS_TERMINADO]

# Edición de la sección Embarque del detalle (saveMaterial en
# accesos/transportista/[id]/page.tsx): proveedor, orden de compra y procedencia.
EMBARQUE_EDITADO = {
    "proveedor_cliente": "Proveedor prueba QA",
    "no_orden_compra": "OC-QA-092",
    "procedencia": "Saltillo",
}

# Imagen que ya existe en preprod (la misma de los tests de Concesionados).
# El back guarda {file_name, file_url} tal cual, sin subir el archivo.
IMAGEN_PREPROD = {
    "file_name": "Libreta.jpg",
    "file_url": "https://b2.linkaform.com/file/app-linkaform/public-client-126/68600/6076166dfd84fa7ea446b917/2026-02-24T23:08:05.png",
}

# Información que llena el transportista en su pase (update_information_transportista):
# foto de licencia del conductor y del ayudante, tarjeta de circulación del
# vehículo y foto de contenedores (TB-108).
INFORMACION_TRANSPORTISTA = {
    "conductor": {"nombre": "Conductor prueba patio", "licencia": "QA-LIC-108", "foto": IMAGEN_PREPROD},
    "ayudante": {"nombre": "Ayudante prueba patio", "licencia": "QA-LIC-108-B", "foto": IMAGEN_PREPROD},
    "vehiculo": {"tipo": "Tractocamión", "marca": "Kenworth", "placas": "QA-PATIO-108", "foto": IMAGEN_PREPROD},
    "foto_contenedores": IMAGEN_PREPROD,
}

# Documento adicional que sube el guardia en el detalle del camión
# (handlePlacaDocFileChange en accesos/transportista/[id]/page.tsx): un
# objeto con el tipo como slug de TIPOS_DOCUMENTO_TRANSPORTISTA (TB-109).
DOCUMENTO_ADICIONAL = dict(IMAGEN_PREPROD, tipo="carta_porte", index=None)

# Material con evidencia, como lo manda la inspección de material del detalle
# (handleGuardar en accesos/transportista/[id]/page.tsx). Sin index para que
# se agregue como fila nueva en un camión sin materiales (TB-110).
MATERIAL_CON_EVIDENCIA = {
    "ref": "vehiculo",
    "producto": "Producto prueba QA",
    "lote": "QA-LOTE-110",
    "cant_esperada": "10",
    "cant_fisica": "10",
    "cant_buena": "10",
    "cant_danada": "",
    "cant_faltante": "",
    "comentario": "Material prueba patio",
    "evidencia": [IMAGEN_PREPROD],
}
