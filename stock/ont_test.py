# -*- coding: utf-8 -*-
import sys, simplejson, copy, time, random, string
from datetime import datetime ,timedelta


from lkf_modules.stock.items.scripts.Stock.stock_utils import Stock

from account_settings import *

from test_utils import TestStock



fecha = datetime.now()
fecha_salida = fecha + timedelta(days=1)
fecha_str = fecha.strftime('%Y-%m-%d')
fecha_salida = fecha_salida.strftime('%Y-%m-%d')
fecha_datetime = fecha.strftime('%Y-%m-%d %H:%M:%S')

import pandas as pd
import random
import string
import time

class TestStock(TestStock):

    stock_obj = Stock(settings, use_api=True)
    supplier_wh_location = 'Telmex'
    product_code = '1468270'
    product_sku = 'F1468270'
    product_name = 'ONT FIBRA'
    cantidad_series = 5
    archivo_carga = {}
    stock_move = []

    def generar_serie_ont(self, longitud=2):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=longitud))

    def create_excel_file(self):
        # Generar series alfanuméricas aleatorias de 12 caracteres
        # Crear DataFrame
        self.generar_serie_ont() 
        epoch_inicial = int(time.time())
        series = [f"{epoch_inicial + i}{self.generar_serie_ont()}" for i in range(TestStock.cantidad_series)]
        # series = [self.generar_serie_ont() for _ in range(TestStock.cantidad_series)]
        print('series', series)
        df = pd.DataFrame({'Serie ONT': series})

        # Guardar a archivo Excel
        ruta_archivo = '/tmp/series_ont.xlsx'
        df.to_excel(ruta_archivo, index=False)

        print('ruta_archivo,', ruta_archivo)
        return ruta_archivo

    def test_ont_mavie_move_in(self):
        warehouse_in = TestStock.stock_warehouse_1
        location_in = TestStock.stock_warehouse_location_1
        product_code = TestStock.product_code
        product_sku = TestStock.product_sku
        product_name = TestStock.product_name
        qty = 1
        metadata = self.recibo_de_material(product_code, product_sku, product_name, warehouse_in, location_in, qty)
        ruta_archivo = self.create_excel_file()
        nueva_ruta = '/tmp/'
        print('ruta_archivo' , ruta_archivo)
        file_url = TestStock.stock_obj.upload_docto(nueva_ruta, ruta_archivo, TestStock.stock_obj.STOCK_IN_ONE_MANY_ONE, TestStock.stock_obj.mf['xls_file'])
        print('file_url' , file_url)
        TestStock.archivo_carga = file_url
        metadata['answers'].update({TestStock.stock_obj.mf['xls_file']:file_url})
        res_create =  TestStock.stock_obj.lkf_api.post_forms_answers(metadata)
        print('res_create',res_create)
        assert res_create['status_code'] == 201
        time.sleep(1)
        print('TERMINO ----test_crea_recepcion_materiales---')
        TestStock.prod_folio_1 = res_create.get('json', {}).get('folio')
        TestStock.prod_id_1 = res_create.get('json', {}).get('id')
        record = TestStock.stock_obj.get_record_by_id(TestStock.prod_id_1)
        print('TERMINO ----test_crea_recepcion_materiales---')
        answers = record['answers']
        print('answers', answers)
        stock_move = answers[TestStock.stock_obj.f['move_group']]
        print('stock_move=', stock_move)
        TestStock.stock_move = stock_move

    def test_stock_move(self):
        print('entra a a stock move',TestStock.stock_move )
        warehouse_in = TestStock.stock_warehouse_1
        location_in = TestStock.stock_warehouse_location_1
        time.sleep(len(TestStock.stock_move)*2.5)
        for smove in TestStock.stock_move:
            status = smove[TestStock.stock_obj.f['stock_move_status']]
            product_code = smove[TestStock.stock_obj.Product.SKU_OBJ_ID][TestStock.stock_obj.f['product_code']]
            product_sku = smove[TestStock.stock_obj.Product.SKU_OBJ_ID][TestStock.stock_obj.f['product_sku']]
            product_lot = smove[TestStock.stock_obj.f['product_lot']]
            qty = smove[TestStock.stock_obj.f['move_group_qty']]
            print('status=', status)
            print('product_lot=', product_lot)
            assert status == 'done'
            self.do_test_stock(product_code, product_sku, product_lot, warehouse_in, location_in, qty, sleep=False)

    def test_move_stock_warehouse(self):
        warehouse_from = TestStock.stock_warehouse_1
        location_from = TestStock.stock_warehouse_location_1
        # stock_location_1_qty = TestStock.stock_location_1_qty
        # print('stock_location_1_qty', stock_location_1_qty)
        warehouse_to = 'Victor Lopez'
        location_to = 'Almacen Cobre'
        move_qty = 1
        product_code = TestStock.product_code
        product_sku = TestStock.product_sku
        product_name = TestStock.product_name
        product_lot = None
        metadata = self.move_metadata(product_code, product_sku, product_lot, warehouse_from, location_from, warehouse_to, location_to, move_qty)
        metadata['answers'].update({TestStock.stock_obj.mf['xls_file']:TestStock.archivo_carga })
        print('metadata', metadata)
        res_create = TestStock.stock_obj.lkf_api.post_forms_answers(metadata)
        print('res_create', res_create)
        assert res_create['status_code'] == 201
        print('TERMINO ----test_move_stock_warehouse---')
        TestStock.salida_folio_1 = res_create.get('json', {}).get('folio')
        TestStock.salida_id_1 = res_create.get('json', {}).get('id')
        record = TestStock.stock_obj.get_record_by_id(TestStock.salida_id_1)
        print('TERMINO ----test_crea_recepcion_materiales---')
        answers = record['answers']
        print('answers', answers)
        stock_move_out = answers[TestStock.stock_obj.f['move_group']]
        print('stock_move=', stock_move_out)
        TestStock.stock_move_out = stock_move_out

    def test_stock_move_out(self):
        print('entra a a test_stock_move_out',TestStock.stock_move_out )
        warehouse_to = 'Victor Lopez'
        location_to = 'Almacen Cobre'
        time.sleep(len(TestStock.stock_move_out)*2.4)
        for smove in TestStock.stock_move_out:
            print('smove', smove)
            print('TestStock.stock_obj.Product.SKU_OBJ_ID', TestStock.stock_obj.Product.SKU_OBJ_ID)
            print('product_code', TestStock.stock_obj.f['product_code'])
            status = smove[TestStock.stock_obj.f['stock_move_status']]
            product_code = smove[TestStock.stock_obj.STOCK_INVENTORY_OBJ_ID][TestStock.stock_obj.f['product_code']]
            product_sku = smove[TestStock.stock_obj.STOCK_INVENTORY_OBJ_ID][TestStock.stock_obj.f['product_sku']]
            product_lot = smove[TestStock.stock_obj.STOCK_INVENTORY_OBJ_ID][TestStock.stock_obj.f['product_lot']]
            qty = smove[TestStock.stock_obj.f['move_group_qty']]
            print('product_code=', product_code)
            print('product_sku=', product_sku)
            print('product_lot=', product_lot)
            print('qty=', qty)
            assert status == 'done'
            self.do_test_stock(product_code, product_sku, product_lot, warehouse_to, location_to, qty, sleep=False)

    def test_ont_mavie_move_in2(self):
        warehouse_in = TestStock.stock_warehouse_1
        location_in = TestStock.stock_warehouse_location_1
        product_code = TestStock.product_code
        product_sku = TestStock.product_sku
        product_name = TestStock.product_name
        qty = 1
        metadata = self.recibo_de_material(product_code, product_sku, product_name, warehouse_in, location_in, qty)
        file_url = TestStock.archivo_carga 
        metadata['answers'].update({TestStock.stock_obj.mf['xls_file']:file_url})
        res_create =  TestStock.stock_obj.lkf_api.post_forms_answers(metadata)
        print('res_create',res_create)
        assert res_create['status_code'] == 400
