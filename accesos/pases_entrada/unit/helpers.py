# coding: utf-8

from datetime import timedelta

from ..data.pases_entrada_data import (
    NOMBRE_PASE_UNIT,
    FOTO_VALIDA,
    IDENTIFICACION_VALIDA,
    ANFITRION_PASE,
    AUTORIZADO_POR,
)


def fecha_hasta(acceso_obj, dias):
    """Fecha "hasta" del pase a `dias` de hoy, con el mismo hoy que usa access_pass_set_status."""
    return (acceso_obj.get_today_format() + timedelta(days=dias)).strftime("%Y-%m-%d 23:59:59")


def answers_pase(acceso_obj, **campos):
    """Answers del pase con los ids de pase_entrada_fields; sin anfitrión en grupo_visitados."""
    answers = {acceso_obj.pase_entrada_fields["grupo_visitados"]: []}
    for campo, valor in campos.items():
        answers[acceso_obj.pase_entrada_fields[campo]] = valor
    return answers


def campos_pase_completo(acceso_obj, dias_vigencia):
    """
    Campos de un pase con todo lo que pide access_pass_set_status: nombre,
    foto, identificación, fecha hasta, a quién visita y quién lo autorizó.
    Cada test quita o cambia solo lo que revisa.
    """
    return {
        "walkin_nombre": NOMBRE_PASE_UNIT,
        "walkin_fotografia": FOTO_VALIDA,
        "walkin_identificacion": IDENTIFICACION_VALIDA,
        "fecha_desde_hasta": fecha_hasta(acceso_obj, dias_vigencia),
        "grupo_visitados": [
            {acceso_obj.CONF_AREA_EMPLEADOS_CAT_OBJ_ID: {acceso_obj.mf["nombre_empleado"]: ANFITRION_PASE}}
        ],
        "catalago_autorizado_por": {acceso_obj.pase_entrada_fields["autorizado_por"]: AUTORIZADO_POR},
    }
