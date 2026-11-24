# coding: utf-8

"""
Datos de los unitarios de Turnos (Inicio/Cierre de caseta: do_checkin,
do_checkout, update_delete_suplente). Los datos viejos de las pruebas e2e
siguen en turns_data.py.
"""

from pases_entrada.data.datos_base import LOCATION, AREA  # noqa: F401

# Ubicación del dispositivo como la mandan la web y la app: el mismo punto en
# los tres formatos que acepta parse_geolocation.
LATITUD = 25.6866
LONGITUD = -100.3161
PUNTO_ESPERADO = [LATITUD, LONGITUD]
GEO_LAT_LONG = {"lat": LATITUD, "long": LONGITUD}
GEO_LATITUDE_LONGITUDE = {"latitude": LATITUD, "longitude": LONGITUD}
GEO_LISTA = [LATITUD, LONGITUD]
# Lo que no es un punto real: 0,0 (la app sin ubicación), fuera de rango,
# texto y lo que no trae los dos valores.
GEO_FALSOS = [{"lat": 0, "long": 0}, {"lat": 91, "long": 0}, {"lat": "norte", "long": "oeste"}, None, [LATITUD]]

# Usuario y empleado que inician turno.
USUARIO_GUARDIA = {"name": "Guardia de prueba QA"}
EMPLEADO_GUARDIA = {"worker_name": "Guardia de prueba QA"}
# Roles que manda el front: uno normal y uno de administración que el
# usuario no tiene asignado.
ROL_GUARDIA = "Guardia"
ROL_ADMIN = "Administrador"
# Turno abierto de la caseta y respuesta del guardado cuando sale bien.
CHECKIN_ABIERTO = {"_id": "000000000000000000000031"}
GUARDADO_OK = {"status_code": 202}
# Tipo del último turno de la caseta (get_last_checkin): abierta o cerrada.
CHECKIN_TIPO_ABIERTA = "abierta"
CHECKIN_TIPO_CERRADA = "cerrada"

# Cerrar turno (do_checkout): id del guardia que sigue dentro del turno y la
# zona con la que se creó el registro.
GUARDIA_ID = 1001
ZONA_TURNO = "America/Monterrey"
ESTATUS_ENTRADA = "entrada"
ESTATUS_SALIDA = "salida"
ASISTENCIA_OK = "Correcto"
# Quitar el suplente (update_delete_suplente): folio del turno abierto del
# usuario y lo que manda el front al borrar el nombre.
FOLIO_TURNO = "1-TURNO"
SUPLENTE_VACIO = ""
SUPLENTE_NOMBRE = "Suplente prueba QA"
