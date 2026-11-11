# coding: utf-8

"""
Helpers de los unitarios de Nuevo Acceso.
"""

from datetime import datetime, timedelta

import pytz


def fecha_relativa(acceso_obj, minutos):
    """Ahora más (o menos) `minutos`, en la zona del usuario y con el formato del pase."""
    ahora = datetime.now(pytz.timezone(acceso_obj.user["timezone"])).replace(tzinfo=None, microsecond=0)
    return (ahora + timedelta(minutes=minutos)).strftime("%Y-%m-%d %H:%M:%S")
