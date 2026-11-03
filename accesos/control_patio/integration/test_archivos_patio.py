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
