# coding: utf-8

import logging, simplejson

from urllib.parse import urlparse

from .fixtures import *
from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import *

import sys, os

print('startoing...')
def test_account_locations(accesos_obj):
    response_location = accesos_obj.catalogos_pase_location()
    ubicaciones_user = response_location['ubicaciones_user']
    res = {}
    for location in ubicaciones_user:
        areas = accesos_obj.catalogos_pase_area(location)
        res[location] = areas['areas_by_location']
    print('rse=',res)
    return res
