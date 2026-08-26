# coding: utf-8
import pytest
from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import Accesos
from account_settings import settings


@pytest.fixture
def acceso_transportista():
    acc = Accesos(settings, use_api=True)
    return acc
