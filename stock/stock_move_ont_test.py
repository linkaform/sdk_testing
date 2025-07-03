# -*- coding: utf-8 -*-
import sys, simplejson, copy, time, random, string
from datetime import datetime ,timedelta


from lkf_modules.stock.items.scripts.Stock.stock_utils import Stock

from account_settings import *

from test_utils import TestStock


print('starting test')
stock_obj = Stock(settings, use_api=True)
print('stock obj', stock_obj)

# lkf_obj = base.LKF_Base(settings)
# lkm = lkf_obj.lkm 
# lkf_api = lkf_obj.lkf_api
# VARS = {}

# # stock_obj = Stock(settings, sys_argv=sys.argv)

# FORM_RECEPCION_MATERIALES = lkm.form_id('recepcion_de_materiales_de_proveedor','id')
# FORM_INVENTORY_ADJUSTMENT = lkm.form_id('stock_inventory_adjustment','id')
# FORM_MOVE_ONE_MANY_ONE = lkm.form_id('stock_move_one_many_one','id')

# CATALOG_WAREHOUSE_LOCATION = lkm.catalog_id('warehouse_locations')
# CATALOG_WAREHOUSE_LOCATION_OBJ_ID = CATALOG_WAREHOUSE_LOCATION.get('obj_id')

# CATALOG_WAREHOUSE_LOCATION_DEST = lkm.catalog_id('warehouse_location_destination')
# CATALOG_WAREHOUSE_LOCATION_DEST_OBJ_ID = CATALOG_WAREHOUSE_LOCATION_DEST.get('obj_id')

# CATALOG_STOCK_INVENTORY = lkm.catalog_id('stock_inventory')
# CATALOG_STOCK_INVENTORY_OBJ_ID = CATALOG_STOCK_INVENTORY.get('obj_id')

# CATALOG_SKU = lkm.catalog_id('sku_catalog')
# CATALOG_SKU_OBJ_ID = CATALOG_SKU.get('obj_id')

fecha = datetime.now()
fecha_salida = fecha + timedelta(days=1)
fecha_str = fecha.strftime('%Y-%m-%d')
fecha_salida = fecha_salida.strftime('%Y-%m-%d')
fecha_datetime = fecha.strftime('%Y-%m-%d %H:%M:%S')

 
class TestStock(TestStock):


    # def test_delete_ont(self):
    #     stock_obj.set_mongo_connections()
    #     stock_obj.ont_cr.delete_many({})
    #     stock_obj.records_cr.delete_many({'form_id':{'$in':[133063,133061,133064]}})

    def test_move_stock_in(self):
        stock_obj.set_mongo_connections()
        stock_obj.ont_cr.delete_many({})
        stock_obj.records_cr.delete_many({'form_id':{'$in':[133063,133061,133064]}})
        warehouse_in = TestStock.stock_warehouse_1
        location_in = TestStock.stock_warehouse_location_1
        product_code = TestStock.ont_code
        product_sku = TestStock.ont_sku
        product_name = TestStock.ont_name
        file_url = "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/6650c41a967ad190e6a76dd3/682d4d99ed7a3bd85bd32ac9.xlsx"
        metadata = self.recibo_de_ont(product_code, product_sku, product_name, warehouse_in, location_in, file_url=file_url)
        res_create =  stock_obj.lkf_api.post_forms_answers(metadata)
        assert res_create['status_code'] == 201
        TestStock.prod_folio_1 = res_create.get('json', {}).get('folio')
        TestStock.prod_id_1 = res_create.get('json', {}).get('id')
        record = stock_obj.get_record_by_id(TestStock.prod_id_1)
        answers = record['answers']
        stock_move = answers[stock_obj.f['move_group']]
        for move in stock_move:
            prod_catalog = move.get(stock_obj.Product.SKU_OBJ_ID)
            product_code = prod_catalog.get(stock_obj.f['product_code'])
            product_sku = prod_catalog.get(stock_obj.f['sku'])
            product_lot = move.get(stock_obj.f['product_lot'])
            qty = self.do_test_stock(product_code, product_sku, product_lot, warehouse_in, location_in, 1 )
        status = stock_move[0][stock_obj.f['stock_move_status']]
        assert status == 'done'

    def test_move_stock_in_ont_repetidas(self):
        warehouse_in = TestStock.stock_warehouse_1
        location_in = TestStock.stock_warehouse_location_1
        product_code = TestStock.ont_code
        product_sku = TestStock.ont_sku
        product_name = TestStock.ont_name
        qty = 1
        file_url = "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/6650c41a967ad190e6a76dd3/682d4d99ed7a3bd85bd32ac9.xlsx"
        metadata = self.recibo_de_ont(product_code, product_sku, product_name, warehouse_in, location_in, file_url=file_url)
        #TODO levantar error de series repetidas con index de base de datos.
        #res_create =  stock_obj.lkf_api.post_forms_answers(metadata)
        #assert res_create['status_code'] == 400
        
    def test_move_stock_warehouse(self):
        warehouse_from = TestStock.stock_warehouse_1
        location_from = TestStock.stock_warehouse_location_1
        warehouse_to = TestStock.stock_warehouse_to
        warehouse_to = TestStock.stock_warehouse_location_to
        location_to = 'Almacen Cobre'
        move_qty = 1
        move_qty2 = 1
        product_code = TestStock.ont_code
        product_sku = TestStock.ont_sku
        product_name = TestStock.ont_name
        product_lot = None
        metadata = self.salida_ont_metadata(
            product_code, 
            product_sku, 
            product_lot, warehouse_from, location_from, warehouse_to, location_to, 
            move_qty,
            move_qty2)
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        assert res_create['status_code'] == 201
        record = stock_obj.get_record_by_id(res_create.get('json', {}).get('id'))
        answers = record['answers']
        stock_move = answers[stock_obj.f['move_group']]
        for move in stock_move:
            prod_catalog = move.get(stock_obj.CATALOG_INVENTORY_OBJ_ID)
            product_code = prod_catalog.get(stock_obj.Product.f['product_code'])
            product_sku = prod_catalog.get(stock_obj.Product.f['product_sku'])
            product_lot = prod_catalog.get(stock_obj.f['product_lot'])
            qty = self.do_test_stock(product_code, product_sku, product_lot, warehouse_to, location_to, move_qty)
            TestStock.stock_move_wh_1_qty = move_qty
            print('1qty', qty)
            print('warehouse_to', warehouse_to)
            print('location_to', location_to)
            print('product_sku', product_sku)
            print('product_lot', product_lot)
            assert qty == move_qty
            print('warehouse_from', warehouse_from)
            print('location_from', location_from)
            qty = self.do_test_stock(product_code, product_sku, product_lot, warehouse_from, location_from, 0 )
            print('qty', qty)
            assert qty  == 0

    # def test_move_stock_in_50(self):
    #     warehouse_in = TestStock.stock_warehouse_1
    #     location_in = TestStock.stock_warehouse_location_1
    #     product_code = TestStock.ont_code
    #     product_sku = TestStock.ont_sku
    #     product_name = TestStock.ont_name
    #     file_url = "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/6650c41a967ad190e6a76dd3/68471d185d4a167c6be11212.xlsx"
    #     metadata = self.recibo_de_ont(product_code, product_sku, product_name, warehouse_in, location_in, file_url=file_url)
    #     res_create =  stock_obj.lkf_api.post_forms_answers(metadata)
    #     assert res_create['status_code'] == 201
    #     TestStock.prod_folio_1 = res_create.get('json', {}).get('folio')
    #     TestStock.prod_id_1 = res_create.get('json', {}).get('id')
    #     record = stock_obj.get_record_by_id(TestStock.prod_id_1)
    #     answers = record['answers']
    #     stock_move = answers[stock_obj.f['move_group']]
    #     for move in stock_move:
    #         prod_catalog = move.get(stock_obj.Product.SKU_OBJ_ID)
    #         product_code = prod_catalog.get(stock_obj.f['product_code'])
    #         product_sku = prod_catalog.get(stock_obj.f['sku'])
    #         product_lot = move.get(stock_obj.f['product_lot'])
    #         #qty = self.do_test_stock(product_code, product_sku, product_lot, warehouse_in, location_in, 1 )
    #     status = stock_move[0][stock_obj.f['stock_move_status']]
    #     assert status == 'done'

    # def test_move_stock_warehouse_50(self):
    #     import random
    #     warehouse_from = TestStock.stock_warehouse_1
    #     location_from = TestStock.stock_warehouse_location_1
    #     warehouse_to = TestStock.stock_warehouse_to
    #     warehouse_to = TestStock.stock_warehouse_location_to
    #     location_to = 'Almacen Cobre'
    #     move_qty = 1
    #     move_qty2 = 1
    #     product_code = TestStock.ont_code
    #     product_sku = TestStock.ont_sku
    #     product_name = TestStock.ont_name
    #     product_lot = None
    #     file_url = "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/6650c41a967ad190e6a76dd3/68471d185d4a167c6be11212.xlsx"
    #     metadata = self.salida_ont_metadata(
    #         product_code, 
    #         product_sku, 
    #         product_lot, warehouse_from, location_from, warehouse_to, location_to, 
    #         move_qty,
    #         move_qty2,**{'file_url': file_url})
    #     res_create = stock_obj.lkf_api.post_forms_answers(metadata)
    #     assert res_create['status_code'] == 201
    #     record = stock_obj.get_record_by_id(res_create.get('json', {}).get('id'))
    #     answers = record['answers']
    #     stock_move = answers[stock_obj.f['move_group']]
    #     for move in stock_move:
    #         if random.random() < 0.7:
    #             continue
    #         prod_catalog = move.get(stock_obj.CATALOG_INVENTORY_OBJ_ID)
    #         product_code = prod_catalog.get(stock_obj.Product.f['product_code'])
    #         product_sku = prod_catalog.get(stock_obj.Product.f['product_sku'])
    #         product_lot = prod_catalog.get(stock_obj.f['product_lot'])
    #         qty = self.do_test_stock(product_code, product_sku, product_lot, warehouse_to, location_to, move_qty)
    #         TestStock.stock_move_wh_1_qty = move_qty
    #         print('1qty', qty)
    #         print('1product_sku', product_sku)
    #         print('product_lot', product_lot)
    #         print('warehouse_to', warehouse_to)
    #         print('location_to', location_to)
    #         assert qty == move_qty
    #         print('warehouse_from', warehouse_from)
    #         print('location_from', location_from)
    #         qty = self.do_test_stock(product_code, product_sku, product_lot, warehouse_from, location_from, 0 )
    #         print('qty', qty)
    #         assert qty  == 0

    # def test_move_stock_in_10024(self):
    #     warehouse_in = TestStock.stock_warehouse_1
    #     location_in = TestStock.stock_warehouse_location_1
    #     product_code = TestStock.ont_code
    #     product_sku = TestStock.ont_sku
    #     product_name = TestStock.ont_name
    #     file_url = "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/6650c41a967ad190e6a76dd3/6850eed4dc61bfed1f80e43b.xlsx"
    #     metadata = self.recibo_de_ont(product_code, product_sku, product_name, warehouse_in, location_in, file_url=file_url)
    #     res_create =  stock_obj.lkf_api.post_forms_answers(metadata)
    #     assert res_create['status_code'] == 201
    #     TestStock.prod_folio_1 = res_create.get('json', {}).get('folio')
    #     TestStock.prod_id_1 = res_create.get('json', {}).get('id')
    #     record = stock_obj.get_record_by_id(TestStock.prod_id_1)
    #     answers = record['answers']
    #     stock_move = answers[stock_obj.f['move_group']]
    #     # for move in stock_move:
    #     #     prod_catalog = move.get(stock_obj.Product.SKU_OBJ_ID)
    #     #     product_code = prod_catalog.get(stock_obj.f['product_code'])
    #     #     product_sku = prod_catalog.get(stock_obj.f['sku'])
    #     #     product_lot = move.get(stock_obj.f['product_lot'])
    #     #     qty = self.do_test_stock(product_code, product_sku, product_lot, warehouse_in, location_in, 1 )
    #     status = stock_move[0][stock_obj.f['stock_move_status']]
    #     assert status == 'done'