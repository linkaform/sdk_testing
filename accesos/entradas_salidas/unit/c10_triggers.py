"""Funciones que disparan los unitarios de esta seccion en ./lkf test.

Si cambia cualquiera de estas funciones, ./lkf test corre TODOS los unitarios
de la seccion (no solo los de esa funcion). Al agregar un unitario de una
funcion que no esta aqui, agregala. Una funcion puede estar en varias
secciones.
"""

C10_TRIGGERS = [
    "bitacora_base_match",
    "do_out",
    "force_quit_all_persons",
    "get_list_bitacora",
]
