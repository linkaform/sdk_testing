"""Funciones que disparan los unitarios de esta seccion en ./lkf test.

Si cambia cualquiera de estas funciones, ./lkf test corre TODOS los unitarios
de la seccion (no solo los de esa funcion). Al agregar un unitario de una
funcion que no esta aqui, agregala. Una funcion puede estar en varias
secciones.

Incidencias la sirve Sanic en prod (incidencias_sdk.py): los tests llevan
@pytest.mark.back("sanic") y en addons salen SKIPPED.
"""

C10_TRIGGERS = [
    "_crear_falla_de_incidencia",
    "_reporta_sesion",
    "_tiempo_cierre_answers",
    "_url_registro_lkf",
    "create_incidence",
    "update_incidence",
]
