"""Funciones que disparan los unitarios de esta seccion en ./lkf test.

Si cambia cualquiera de estas funciones, ./lkf test corre TODOS los unitarios
de la seccion (no solo los de esa funcion). Al agregar un unitario de una
funcion que no esta aqui, agregala. Una funcion puede estar en varias
secciones.

Rondines lo sirve Sanic en prod (rondines_sdk.py): los unitarios llevan
@pytest.mark.back("sanic") y en addons salen SKIPPED.
"""

C10_TRIGGERS = [
    "claim_group_rondin",
    "claim_rondin",
    "create_recorrido_rondin",
    "pause_or_play_rondin",
    "rondin_asignado_a",
]
