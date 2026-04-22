# Estructura esperada de la respuesta de get_config_accesos()
# Usada como referencia para validar los tests de integración.
# NO es un mock — es documentación de la forma real de los datos.

EXPECTED_MENU_KEYS = {"menus", "group_name", "alertas", "exclude_inputs", "include_inputs"}

VALID_MENUS = ['bitacoras', 'accesos', 'notas', 'pases', 'turnos', 'rondines', 'incidencias', 'articulos']

EXPECTED_ALERTA_KEYS = {"accion"}