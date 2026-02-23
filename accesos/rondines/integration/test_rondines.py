# coding: utf-8

import logging, simplejson

from urllib.parse import urlparse

from .fixtures import *
from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import *

import sys, os

print('startoing...')
def test_account_locations(accesos_obj, mock_locations):
    for location, areas in mock_locations.items():
        print('location', location)
        areas = accesos_obj.get_catalog_areas(ubicacion=location)
        print('aresa', areas)
        for area in areas:
            assert area in mock_locations[location]

def test_create_rondin(accesos_obj, mock_crear_rondin):
    rondin_data = mock_crear_rondin.get('rondin_data')
    res = accesos_obj.create_rondin(rondin_data=rondin_data)
    print('res', res)
