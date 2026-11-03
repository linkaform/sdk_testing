# coding: utf-8

"""
Archivos de Control de patio: fotos que llena el transportista en su pase
(update_information_transportista), documentos adicionales y evidencia de
materiales del registro del patio (save_bitac_transportista_record).
Notion: TB-108 a TB-110.
"""

import pytest

from .fixtures import *
from ..data.control_patio_data import (
    ESTATUS_DESCARTADO,
    IMAGEN_PREPROD,
    INFORMACION_TRANSPORTISTA,
    DOCUMENTO_ADICIONAL,
    MATERIAL_CON_EVIDENCIA,
)


@pytest.mark.integration
def test_fotos_del_transportista_se_guardan_en_el_pase(patio_obj, mock_pase_transportista):
    """
    TB-108: las fotos que sube el transportista en su pase (licencia del
    conductor y del ayudante, tarjeta de circulación y contenedores) deben
    guardarse y regresar en el pase con su file_url. Si se pierden, el guardia
    no puede revisar los documentos del camión al llegar.
    """
    res_pase = patio_obj.create_pass_transportista(mock_pase_transportista)
    pase_id = (res_pase.get("json") or {}).get("id")
    assert pase_id, f"No se creó el pase de transportista: {res_pase}"

    try:
        patio_obj.update_information_transportista(dict(INFORMACION_TRANSPORTISTA, record_id=pase_id))

        pase = patio_obj.get_pass_transportista(record_id=pase_id)
        for campo in ("conductor_foto_licencia", "ayudante_foto_licencia", "vehiculo_tarjeta_circulacion", "foto_contenedores"):
            urls = [foto.get("file_url") for foto in pase.get(campo) or []]
            assert urls == [IMAGEN_PREPROD["file_url"]], f"{campo} quedó con {urls}"
    finally:
        # Saca del patio el registro 'programado' que deja el pase.
        programado_id = patio_obj.get_pass_transportista(record_id=pase_id).get("bitacora_id")
        if programado_id:
            patio_obj.save_bitac_transportista_record(programado_id, {"estatus": ESTATUS_DESCARTADO})


@pytest.mark.integration
def test_documento_adicional_se_guarda_en_el_registro_del_patio(patio_obj, camion_en_arribo):
    """
    TB-109: un documento que sube el guardia en el detalle del camión (por
    ejemplo la carta porte) debe quedar en el registro del patio con su tipo
    y su archivo. Si no, el documento no aparece en el detalle.
    """
    record_id = camion_en_arribo

    patio_obj.save_bitac_transportista_record(record_id, {"documentos_adicionales": DOCUMENTO_ADICIONAL})

    documentos = patio_obj.get_bitac_transportista_record(record_id).get("documentos") or []
    guardados = [
        d for d in documentos
        if any(a.get("file_url") == IMAGEN_PREPROD["file_url"] for a in d.get("documento") or [])
    ]
    assert len(guardados) == 1, f"El documento no quedó en el registro: {documentos}"
    assert guardados[0].get("tipo") == DOCUMENTO_ADICIONAL["tipo"], f"El documento quedó con tipo {guardados[0].get('tipo')!r}"
    assert guardados[0]["documento"][0].get("file_name") == IMAGEN_PREPROD["file_name"]


@pytest.mark.integration
def test_evidencia_del_material_se_guarda_en_el_registro_del_patio(patio_obj, camion_en_arribo):
    """
    TB-110: la evidencia (foto) de un material en la inspección de material
    debe quedar en el registro del patio con su file_url. Si se pierde, no
    hay prueba del estado en que llegó el material.
    """
    record_id = camion_en_arribo

    patio_obj.save_bitac_transportista_record(record_id, {"materiales": [MATERIAL_CON_EVIDENCIA]})

    materiales = patio_obj.get_bitac_transportista_record(record_id).get("materiales") or []
    guardados = [m for m in materiales if m.get("lote") == MATERIAL_CON_EVIDENCIA["lote"]]
    assert len(guardados) == 1, f"El material no quedó en el registro: {materiales}"
    urls = [e.get("file_url") for e in guardados[0].get("evidencia") or []]
    assert urls == [IMAGEN_PREPROD["file_url"]], f"La evidencia del material quedó con {urls}"
