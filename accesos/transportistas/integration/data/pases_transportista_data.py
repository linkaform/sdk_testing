# coding: utf-8
import random
from datetime import datetime, timedelta
from pytz import timezone


def _date_str(days_offset=0):
    dt = datetime.now().astimezone(timezone('America/Monterrey'))
    dt += timedelta(days=days_offset)
    return dt.strftime('%Y-%m-%d')


_DOC_URL = "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/116852/660459dde2b2d414bce9cf8f/6a1f5e2583d26c012355f8ae.pdf"

def _doc(tipo):
    return {
        "tipo_de_documento": tipo,
        "documento_transportista": [{"file_name": f"{tipo}.pdf", "file_url": _DOC_URL}]
    }


_PROVEEDORES = [
    "Plastipack de México S.A.",
    "Proveedora Norteña S.A.",
    "Distribuidora Central S.A.",
    "Suministros del Norte S.A.",
    "Polímeros del Bajío S.A.",
    "Industrias Químicas del Pacífico S.A.",
]

_MATERIALES = [
    "Resina PET virgen",
    "Polietileno de alta densidad",
    "PVC granulado",
    "Nylon 6",
    "Polipropileno",
    "Masterbatch negro",
]

_TRANSPORTISTAS = [
    "Fletes del Bajío S.A.",
    "Transportes Rápidos S.A.",
    "Carga Rápida S.A.",
    "Logística Express S.A.",
    "Autotransportes del Norte S.A.",
    "Carga Pesada del Pacífico S.A.",
]

_LETRAS = "ABCDEFGHJKLMNPRSTUVWXYZ"

def _orden_compra():
    return f"OC-2026-{random.randint(1000, 9999)}"

def _placas():
    letras = "".join(random.choices(_LETRAS, k=3))
    numeros = random.randint(100, 999)
    sufijo = random.choice(_LETRAS)
    return f"{letras}-{numeros}-{sufijo}"

def _base(cantidad):
    return {
        "tipo_de_operacion": "entrega_de_materia_prima",
        "creado_desde": "testing",
        "proveedor_y_material": {
            "proveedor": random.choice(_PROVEEDORES),
            "material": random.choice(_MATERIALES),
            "cantidad": cantidad,
            "orden_compra": _orden_compra(),
        },
        "transportista": {
            "nombre": random.choice(_TRANSPORTISTAS),
            "placas_vehiculo": _placas(),
        },
    }


# Andén 1 — fecha_desde y fecha_hasta, con horario, 1 documento
PASE_ANDEN_1_COMPLETO = {
    **_base(20),
    "programacion": {
        "fecha_pase_transportista_desde": _date_str(1),
        "fecha_pase_transportista_hasta": _date_str(5),
        "horario_disponible": "08:00-10:00",
        "anden": "Andén 1"
    },
    "documentos": [_doc("factura")]
}

# Andén 2 — sin fecha_hasta, con horario, 1 documento
PASE_ANDEN_2_SIN_FECHA_HASTA = {
    **_base(15),
    "programacion": {
        "fecha_pase_transportista_desde": _date_str(2),
        "fecha_pase_transportista_hasta": "",
        "horario_disponible": "10:00-12:00",
        "anden": "Andén 2"
    },
    "documentos": [_doc("factura")]
}

# Andén 3 — fecha_desde y fecha_hasta, sin horario, 1 documento
PASE_ANDEN_3_SIN_HORARIO = {
    **_base(50),
    "programacion": {
        "fecha_pase_transportista_desde": _date_str(3),
        "fecha_pase_transportista_hasta": _date_str(7),
        "horario_disponible": "",
        "anden": "Andén 3"
    },
    "documentos": [_doc("factura")]
}

# Andén 1 — sin fecha_hasta, sin horario, múltiples documentos
PASE_ANDEN_1_SIN_FECHA_HASTA_SIN_HORARIO = {
    **_base(8),
    "programacion": {
        "fecha_pase_transportista_desde": _date_str(1),
        "fecha_pase_transportista_hasta": "",
        "horario_disponible": "",
        "anden": "Andén 1"
    },
    "documentos": [_doc("factura"), _doc("carta_porte")]
}

# Andén 2 — fecha_desde distinta, con horario, múltiples documentos
PASE_ANDEN_2_MULTIPLES_DOCUMENTOS = {
    **_base(30),
    "programacion": {
        "fecha_pase_transportista_desde": _date_str(4),
        "fecha_pase_transportista_hasta": _date_str(9),
        "horario_disponible": "14:00-16:00",
        "anden": "Andén 2"
    },
    "documentos": [_doc("factura"), _doc("carta_porte"), _doc("remision")]
}

# Andén 3 — sin documentos
PASE_ANDEN_3_SIN_DOCUMENTOS = {
    **_base(5),
    "programacion": {
        "fecha_pase_transportista_desde": _date_str(2),
        "fecha_pase_transportista_hasta": _date_str(6),
        "horario_disponible": "07:00-09:00",
        "anden": "Andén 3"
    },
    "documentos": []
}
