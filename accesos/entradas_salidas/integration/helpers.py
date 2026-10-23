# coding: utf-8

"""
Helpers para las pruebas de integración de Entradas & Salidas.
Pegan contra la API/BD real (preprod) a través de `acceso_obj`.

Para crear y activar pases se reutilizan los helpers de passes/integration.
"""

from passes.integration.helpers import crear_pase, completar_pase_activo  # noqa: F401


def obtener_registro_bitacora(acceso_obj, qr_code):
    """
    Lee directo de BITACORA_ACCESOS el registro más reciente (por created_at)
    del pase `qr_code` y regresa sus campos clave ya aplanados.

    Se ordena por created_at a propósito: do_out busca por updated_at
    (get_last_user_move) y aquí queremos verificar contra la visita real,
    no contra lo que el código cree que es la última.
    """
    mf = acceso_obj.mf
    cursor = acceso_obj.cr.find({
        "form_id": acceso_obj.BITACORA_ACCESOS,
        "deleted_at": {"$exists": False},
        f"answers.{mf['codigo_qr']}": qr_code,
    }).sort("created_at", -1).limit(1)
    docs = list(cursor)
    assert docs, f"No hay registro de bitácora para el pase {qr_code}"
    return _aplanar_registro(acceso_obj, docs[0])


def obtener_registro_bitacora_por_id(acceso_obj, record_id):
    """Igual que obtener_registro_bitacora pero por _id del registro."""
    from bson import ObjectId
    doc = acceso_obj.cr.find_one({"_id": ObjectId(record_id)})
    assert doc, f"No existe el registro de bitácora {record_id}"
    return _aplanar_registro(acceso_obj, doc)


def _aplanar_registro(acceso_obj, doc):
    mf = acceso_obj.mf
    answers = doc.get("answers", {})
    areas_entrada = answers.get(acceso_obj.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID, {}) or {}
    areas_salida = answers.get(acceso_obj.AREAS_DE_LAS_UBICACIONES_SALIDA_OBJ_ID, {}) or {}
    return {
        "_id": str(doc["_id"]),
        "folio": doc.get("folio"),
        "tipo_registro": answers.get(mf["tipo_registro"]),
        "fecha_entrada": answers.get(mf["fecha_entrada"]),
        "fecha_salida": answers.get(mf["fecha_salida"]),
        "duracion": answers.get(mf["duracion"]),
        "ubicacion": areas_entrada.get(mf["ubicacion"]),
        "nombre_area_salida": areas_salida.get(mf["nombre_area_salida"]),
        "status_gafete": answers.get(mf["status_gafete"]),
    }


def dar_entrada(acceso_obj, qr_code, location, area):
    """Registra la entrada (do_access) y regresa el registro de bitácora creado."""
    res = acceso_obj.do_access(qr_code, location, area, {})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada a {qr_code}: {res}"
    registro = obtener_registro_bitacora(acceso_obj, qr_code)
    assert registro["tipo_registro"] == "entrada", f"La entrada no quedó registrada: {registro}"
    return registro


def salida_silenciosa(acceso_obj, qr_code, location, area, record_id=None):
    """
    Limpieza: intenta registrar la salida e ignora el error si la persona ya
    no está dentro. Evita dejar entradas abiertas en preprod que bloqueen
    otros tests (validate_access_pass_location). Con `record_id` apunta a
    una visita específica.
    """
    try:
        acceso_obj.do_out(qr_code, location, area, record_id=record_id)
    except Exception:
        pass


def gafete_y_locker_disponibles(acceso_obj, location, area):
    """
    Busca un gafete y un locker de identificaciones 'Disponible' en la caseta.
    Regresa (gafete_id, locker_id) o (None, None) si la cuenta no tiene.
    """
    gafetes = acceso_obj.get_gafetes(status="Disponible", location=location, area=area, limit=1)
    lockers = acceso_obj.get_lockers(
        status="Disponible", location=location, area=area, tipo_locker="Identificaciones", limit=1
    )
    if not gafetes or not lockers:
        return None, None
    return gafetes[0]["gafete_id"], lockers[0]["locker_id"]
