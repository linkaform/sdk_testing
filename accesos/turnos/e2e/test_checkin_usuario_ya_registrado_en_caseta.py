import pytest, logging, simplejson
import copy

from turnos.data.turns_data import TURN_DATA_10

@pytest.mark.e2e
def test_checkin_usuario_ya_registrado_en_caseta(accesos_api):
    """
    Valida que el sistema rechaza un segundo checkin del mismo usuario
    que ya tiene un turno abierto en la misma caseta.

    Flujo:
        1. Si hay turno abierto: intenta abrir otro y verifica la excepción.
        2. Si no hay turno abierto: abre uno, luego intenta abrir otro y verifica la excepción.
           Al finalizar cierra el turno abierto como cleanup.
    """
    logging.info('================> Arranca TEST: test_checkin_usuario_ya_registrado_en_caseta')
    checkin_id = None

    try:
        # Paso 1: intentar abrir turno (puede que ya haya uno abierto o no)
        try:
            result = accesos_api.do_checkin(**copy.deepcopy(TURN_DATA_10))
            assert result.get("status_code") in [200, 201, 202], f"Error al abrir turno inicial: {result.get('status_code')}"
            checkin_id = result.get("json", {}).get("id")
            logging.info(f'Paso 1: Turno abierto exitosamente. checkin_id={checkin_id}')
        except Exception as e:
            error = simplejson.loads(str(e)).get("exception", {})
            assert error.get("status") == 400, f"Error inesperado al abrir turno inicial: {error}"
            logging.info('Paso 1: Ya existía un turno abierto, se omite apertura.')

        # Paso 2: intentar abrir turno nuevamente — debe rechazarse
        logging.info('Paso 2: Intentando abrir turno duplicado...')
        with pytest.raises(Exception) as exc_info:
            accesos_api.do_checkin(**copy.deepcopy(TURN_DATA_10))

        error = simplejson.loads(str(exc_info.value)).get("exception", {})
        assert error.get("status") == 400, f"Se esperaba status 400, se obtuvo: {error.get('status')}"
        assert error.get("type") == "warning", f"Se esperaba type 'warning', se obtuvo: {error.get('type')}"
        logging.info(f'Paso 2: Excepción esperada recibida correctamente: {error.get("msg")}')

    finally:
        if checkin_id:
            logging.info('Cleanup: cerrando turno abierto por el test...')
            accesos_api.do_checkout(checkin_id=checkin_id, **{k: v for k, v in TURN_DATA_10.items() if k != 'checkin_id'})
        
