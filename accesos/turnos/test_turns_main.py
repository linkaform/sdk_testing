# Notas importantes:
# Arrancar pruebas unitarias
# ./lkf start test
# hay que checar que esten en modulos y test en ramas iguales
# en test debes de tener una rama por cliente

# -*- coding: utf-8 -*-
import sys, simplejson, copy, random, string, math, json, time, pytz, pytest, logging
from datetime import datetime ,timedelta
from bson import ObjectId
import concurrent.futures

from lkf_modules.accesos.items.scripts.Accesos.accesos_utils import Accesos

from account_settings import *

# Configuracion del logging para los logs al ejecutar pytest
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)

class TestAccesos:
    
    def setup_method(self):
        self.accesos = Accesos(settings, use_api=True)

    def test_number_one(self):
        logging.info('Arranca test #1: .')