import pytest
 
from .fixtures import *
from .helpers import crear_pase
from .data.do_access_data import FOTO_VALIDA, IDENTIFICACION_VALIDA
 
VEHICULO_VALIDO = {
    "tipo_vehiculo": "Automovil",
    "marca_vehiculo": "Nissan",
    "modelo_vehiculo": "Sentra",
    "estado": "Nuevo Leon",
    "placas_vehiculo": "ABC-123",
    "color_vehiculo": "Rojo",
}
 
EQUIPO_VALIDO = {
    "tipo_equipo": "Laptop",
    "nombre_articulo": "Laptop de trabajo",
    "marca_articulo": "Dell",
    "modelo_articulo": "Latitude 5420",
    "color_articulo": "Negro",
    "numero_serie": "SN-000111",
}

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

@pytest.mark.integration
def test_update_pass_completar_con_vehiculo(acceso_obj, mock_pase_do_access):
    """
    Completar un pase con vehiculo.
 
    access_pass_set_status no evalua vehiculo/equipo como requisito (solo
    foto/identificacion), asi que el pase debe quedar 'activo' igual que sin
    vehiculo. Este test confirma ademas que grupo_vehiculos se guarda y se
    regresa correctamente via get_detail_access_pass (formateado por
    format_vehiculos_simple).
    """
    folio = crear_pase(acceso_obj, mock_pase_do_access)
 
    response = acceso_obj.update_pass(
        {
            "walkin_fotografia": FOTO_VALIDA,
            "walkin_identificacion": IDENTIFICACION_VALIDA,
            "grupo_vehiculos": [VEHICULO_VALIDO],
        },
        folio,
    )
    assert response.get('status_code') == 202, (
        f"No se pudo completar el pase {folio} con vehiculo: {response}"
    )
 
    detalle = acceso_obj.get_detail_access_pass(folio)
    assert detalle.get('estatus') == 'activo', (
        f"Se esperaba que el pase quedara 'activo' al completarlo con "
        f"vehiculo (vehiculo no es requisito de activacion), se obtuvo: "
        f"{detalle.get('estatus')!r}"
    )
 
    vehiculos = detalle.get('grupo_vehiculos') or []
    assert len(vehiculos) == 1, (
        f"Se esperaba 1 vehiculo guardado en grupo_vehiculos, se obtuvo: "
        f"{vehiculos!r}"
    )
    vehiculo = vehiculos[0]
    assert vehiculo.get('placas_vehiculo') == 'ABC-123', (
        f"Las placas del vehiculo no coinciden, se obtuvo: {vehiculo!r}"
    )
    assert vehiculo.get('marca_vehiculo') == 'Nissan', (
        f"La marca del vehiculo no coincide, se obtuvo: {vehiculo!r}"
    )
 
 
@pytest.mark.integration
def test_update_pass_completar_con_vehiculo_y_equipo(acceso_obj, mock_pase_do_access):
    """
    Completar un pase con vehiculo y equipo.
    Este test confirma que tanto grupo_vehiculos como
    grupo_equipos se guardan y se regresan correctamente.
    """
    folio = crear_pase(acceso_obj, mock_pase_do_access)
 
    response = acceso_obj.update_pass(
        {
            "walkin_fotografia": FOTO_VALIDA,
            "walkin_identificacion": IDENTIFICACION_VALIDA,
            "grupo_vehiculos": [VEHICULO_VALIDO],
            "grupo_equipos": [EQUIPO_VALIDO],
        },
        folio,
    )
    assert response.get('status_code') == 202, (
        f"No se pudo completar el pase {folio} con vehiculo y equipo: {response}"
    )
 
    detalle = acceso_obj.get_detail_access_pass(folio)
    assert detalle.get('estatus') == 'activo', (
        f"Se esperaba que el pase quedara 'activo' al completarlo con "
        f"vehiculo y equipo (ninguno es requisito de activacion), se "
        f"obtuvo: {detalle.get('estatus')!r}"
    )
 
    vehiculos = detalle.get('grupo_vehiculos') or []
    equipos = detalle.get('grupo_equipos') or []
    assert len(vehiculos) == 1, (
        f"Se esperaba 1 vehiculo guardado en grupo_vehiculos, se obtuvo: "
        f"{vehiculos!r}"
    )
    assert len(equipos) == 1, (
        f"Se esperaba 1 equipo guardado en grupo_equipos, se obtuvo: "
        f"{equipos!r}"
    )
    equipo = equipos[0]
    assert equipo.get('numero_serie') == 'SN-000111', (
        f"El numero de serie del equipo no coincide, se obtuvo: {equipo!r}"
    )
    assert equipo.get('nombre_articulo') == 'Laptop de trabajo', (
        f"El nombre del equipo no coincide, se obtuvo: {equipo!r}"
    )
 
 
@pytest.mark.integration
def test_update_pass_completar_sin_identificacion_no_activa(acceso_obj, mock_pase_do_access):
    """
    Completar un pase sin identificacion -> Pase creado con identificacion
    obligatoria -> Tiene que dar la validacion.
 
    mock_pase_do_access usa 'Planta Monterrey', ubicacion que requiere tanto
    foto como identificacion (confirmado en tests previos de create_access_pass).
    Si el update_pass solo manda foto (sin identificacion), el pase NO debe
    quedar activo: debe permanecer en 'proceso', ya que access_pass_set_status
    exige identificacion cuando la ubicacion la requiere.
    """
    folio = crear_pase(acceso_obj, mock_pase_do_access)
 
    response = acceso_obj.update_pass(
        {
            "walkin_fotografia": FOTO_VALIDA,
        },
        folio,
    )
    assert response.get('status_code') == 202, (
        f"No se pudo actualizar el pase {folio}: {response}"
    )
 
    detalle = acceso_obj.get_detail_access_pass(folio)
    assert detalle.get('estatus') == 'proceso', (
        f"Se esperaba que el pase permaneciera en 'proceso' al faltar "
        f"identificacion (obligatoria en Planta Monterrey), se obtuvo: "
        f"{detalle.get('estatus')!r} (detalle completo: {detalle})"
    )