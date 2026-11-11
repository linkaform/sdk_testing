# coding: utf-8

from datetime import timedelta


def fecha_hasta(acceso_obj, dias):
    """Fecha "hasta" del pase a `dias` de hoy, con el mismo hoy que usa access_pass_set_status."""
    return (acceso_obj.get_today_format() + timedelta(days=dias)).strftime("%Y-%m-%d 23:59:59")


def answers_pase(acceso_obj, **campos):
    """Answers del pase con los ids de pase_entrada_fields; sin anfitrión en grupo_visitados."""
    answers = {acceso_obj.pase_entrada_fields["grupo_visitados"]: []}
    for campo, valor in campos.items():
        answers[acceso_obj.pase_entrada_fields[campo]] = valor
    return answers
