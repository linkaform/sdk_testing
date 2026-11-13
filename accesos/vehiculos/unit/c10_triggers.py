"""Funciones que disparan los unitarios de esta seccion en ./lkf test.

Si cambia cualquiera de estas funciones, ./lkf test corre TODOS los unitarios
de la seccion (no solo los de esa funcion). Al agregar un unitario de una
funcion que no esta aqui, agregala. Una funcion puede estar en varias
secciones.
"""

C10_TRIGGERS = [
    "_answers_vehiculos",
    "_answers_vehiculos_pase",
    "_size_vehiculos_con_tipo",
    "format_vehiculos_simple",
    "get_list_bitacora",
]
