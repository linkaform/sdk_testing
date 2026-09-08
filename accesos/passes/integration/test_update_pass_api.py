import pytest
 
from .fixtures import *
from .helpers import crear_pase
from .data.do_access_data import FOTO_VALIDA, IDENTIFICACION_VALIDA
 
 
@pytest.mark.integration
def test_update_pass_completar_con_foto_e_identificacion(acceso_obj, mock_pase_do_access):
    """
    T-C10-034: Completar un pase con identificacion y fotografia.
 
    'visita_a' ya viene incluido desde la creacion del pase (mock_pase_do_access
    / PASE_ACCESO_BASE trae visita_a=['Usuario Actual']), asi que el update_pass
    para completar el pase solo debe mandar walkin_fotografia +
    walkin_identificacion 
    """
    folio = crear_pase(acceso_obj, mock_pase_do_access)
 
    detalle_inicial = acceso_obj.get_detail_access_pass(folio)
    assert detalle_inicial.get('estatus') == 'proceso', (
        f"Se esperaba que el pase recien creado quedara en 'proceso' antes "
        f"de completarlo, se obtuvo: {detalle_inicial.get('estatus')!r}"
    )
    assert detalle_inicial.get('visita_a'), (
        f"Se esperaba que 'visita_a' ya viniera poblado desde la creacion del "
        f"pase (aunque venga hidratado a los datos del contacto real, no al "
        f"valor crudo enviado), se obtuvo: {detalle_inicial.get('visita_a')!r}"
    )
 
    response = acceso_obj.update_pass(
        {
            "walkin_fotografia": FOTO_VALIDA,
            "walkin_identificacion": IDENTIFICACION_VALIDA,
        },
        folio,
    )
    assert response.get('status_code') == 202, (
        f"No se pudo completar el pase {folio}: {response}"
    )
 
    detalle = acceso_obj.get_detail_access_pass(folio)
    assert detalle.get('estatus') == 'activo', (
        f"Se esperaba que el pase quedara 'activo' tras completar foto e "
        f"identificacion (usando el visita_a heredado de la creacion), se "
        f"obtuvo: {detalle.get('estatus')!r} (detalle completo: {detalle})"
    )