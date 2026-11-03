# coding: utf-8

"""
Lista del día de Control de patio en la app: get_bitac_transportista_records
con solo 'fecha', llamada por la API de scripts igual que la app (el
parámetro lo lee el dispatcher del script, no el método).
Notion: TB-094.
"""

from datetime import datetime

import pytest
import pytz

from .fixtures import *
from ..data.lista_dia_data import PETICION_LISTA_DIA_APP


@pytest.mark.integration
def test_lista_del_dia_de_la_app_solo_trae_camiones_de_ese_dia(patio_obj, camion_en_arribo):
    """
    TB-094: la tarjeta de Control de patio de la app pide la lista solo con
    la fecha de hoy. Debe traer el camión que llegó hoy y ningún camión de
    otro día. Si trae todo el histórico, el guardia ve en el patio camiones
    que ya no están.
    """
    hoy = datetime.now(pytz.timezone(patio_obj.user["timezone"])).strftime("%Y-%m-%d")

    res = patio_obj.lkf_api.run_script(dict(PETICION_LISTA_DIA_APP, fecha=hoy))
    assert res.get("status_code") == 200, f"La lista del día respondió con error: {res}"
    # Igual que la app: la lista viene en response.data (o en data).
    cuerpo = res.get("json") or {}
    registros = (cuerpo.get("response") or {}).get("data", cuerpo.get("data")) or []

    assert camion_en_arribo in {r.get("_id") for r in registros}, "El camión que llegó hoy no está en la lista del día"
    de_otro_dia = [r for r in registros if not (r.get("fecha_hora_ingreso") or "").startswith(hoy)]
    assert not de_otro_dia, (
        f"La lista del {hoy} trae {len(de_otro_dia)} de {len(registros)} camiones de otros días, "
        f"p. ej. ingreso {de_otro_dia[0].get('fecha_hora_ingreso')!r}"
    )
