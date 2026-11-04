# coding: utf-8

"""
Salida de un grupo desde la pantalla de Accesos (do_out). El front y la app
mandan selected_passes con los acompañantes, pero script_turnos.py llama
do_out(qr_code, location, area, gafete_id, record_id) sin ese campo.
Notion: TB-086.
"""

import pytest

from .fixtures import *
from ..data.nuevo_acceso_data import LOCATION, AREA
from passes.integration.helpers import crear_pase, completar_pase_activo, obtener_qr_hijos
from entradas_salidas.integration.helpers import ultima_visita, salida_silenciosa


@pytest.mark.integration
def test_salida_grupal_saca_tambien_a_los_acompanantes(acceso_obj, mock_pase_grupo):
    """
    TB-086: tras el ingreso del titular con sus 2 acompañantes, Registrar
    Salida del grupo debe cerrar la visita de los 3. Si solo sale el
    titular, los acompañantes se quedan "dentro" en la bitácora.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_grupo)
    acompanantes = obtener_qr_hijos(acceso_obj, pase_id)
    assert len(acompanantes) == 2, f"El pase de grupo no creó 2 acompañantes: {acompanantes}"
    for qr in [pase_id] + acompanantes:
        completar_pase_activo(acceso_obj, qr)

    # Ingreso grupal con el formato que manda el front web.
    seleccionados = [{"id": qr, "equipo_vehiculo": []} for qr in acompanantes]
    ingreso = acceso_obj.do_access(pase_id, LOCATION, AREA, {"selected_passes": seleccionados})
    assert all(a["status"] == "success" for a in ingreso["accesos"]), f"Ingreso grupal incompleto: {ingreso}"

    try:
        # Salida como la ejecuta script_turnos.py (option 'do_out').
        acceso_obj.do_out(pase_id, LOCATION, AREA)

        assert ultima_visita(acceso_obj, pase_id)["status_visita"] == "salida", "El titular no salió"
        dentro = [qr for qr in acompanantes if ultima_visita(acceso_obj, qr)["status_visita"] != "salida"]
        assert not dentro, f"Los acompañantes {dentro} siguen dentro tras la salida del grupo"
    finally:
        for qr in [pase_id] + acompanantes:
            salida_silenciosa(acceso_obj, qr, LOCATION, AREA)
