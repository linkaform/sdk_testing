# coding: utf-8

"""
Aviso al destinatario de que llegó su paquete (_notificar_paquete_recibido)
sin mandar correos reales: se revisa qué pasa cuando falta el email.
Notion: TB-249.
"""

import pytest

from ..data.paqueteria_data import PAQUETE_UNIT, AVISO_SIN_EMAIL


@pytest.mark.unit
def test_aviso_por_correo_sin_email_reporta_el_error_y_no_se_envia(accesos_no_api, mocker):
    """
    TB-249: con el canal correo y sin email del destinatario, el aviso debe
    reportar "Sin email del destinatario" para el correo y no intentar
    enviarlo. Si intenta enviarlo, truena o el guardia cree que se avisó.
    """
    enviar = mocker.patch.object(accesos_no_api, "send_email_notification")

    resultado = accesos_no_api._notificar_paquete_recibido(dict(PAQUETE_UNIT), dict(AVISO_SIN_EMAIL))

    assert resultado["correo"] == {"ok": False, "error": "Sin email del destinatario"}
    enviar.assert_not_called()
