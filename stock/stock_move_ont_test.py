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

    def test_move_stock_in(self):
        warehouse_in = TestStock.stock_warehouse_1
        location_in = TestStock.stock_warehouse_location_1
        product_code = TestStock.ont_code
        product_sku = TestStock.ont_sku
        product_name = TestStock.ont_name
        qty = 1
        metadata = self.recibo_de_ont(product_code, product_sku, product_name, warehouse_in, location_in, qty)
        res_create =  stock_obj.lkf_api.post_forms_answers(metadata)
        print('res_create',res_create)
        assert res_create['status_code'] == 201
        time.sleep(1)
        print('TERMINO ----test_crea_recepcion_materiales---')
        TestStock.prod_folio_1 = res_create.get('json', {}).get('folio')
        TestStock.prod_id_1 = res_create.get('json', {}).get('id')
        record = stock_obj.get_record_by_id(TestStock.prod_id_1)
        answers = record['answers']
        print('answers', answers)
        stock_move = answers[stock_obj.f['move_group']]
        for move in stock_move:
            prod_catalog = move.get(stock_obj.Product.SKU_OBJ_ID)
            product_code = prod_catalog.get(stock_obj.f['product_code'])
            product_sku = prod_catalog.get(stock_obj.f['sku'])
            product_lot = move.get(stock_obj.f['product_lot'])
            qty = self.do_test_stock(product_code, product_sku, product_lot, warehouse_in, location_in, 1 )
        print('stock_move=', stock_move)
        status = stock_move[0][stock_obj.f['stock_move_status']]
        print('status=', status)
        assert status == 'done'

        
            

    # def test_move_stock_warehouse(self):
    #     warehouse_from = TestStock.stock_warehouse_1
    #     location_from = TestStock.stock_warehouse_location_1
    #     # stock_location_1_qty = TestStock.stock_location_1_qty
    #     # print('stock_location_1_qty', stock_location_1_qty)
    #     warehouse_to = TestStock.stock_warehouse_to
    #     warehouse_to = TestStock.stock_warehouse_location_to
    #     location_to = 'Almacen Cobre'
    #     move_qty = 300
    #     move_qty2 = 400
    #     product_code = TestStock.product_code
    #     product_sku = TestStock.product_sku
    #     product_name = TestStock.product_name
    #     product_lot = TestStock.product_lot
    #     metadata = self.move_metadata(
    #         product_code, 
    #         product_sku, 
    #         product_lot, warehouse_from, location_from, warehouse_to, location_to, 
    #         move_qty,
    #         move_qty2)
    #     res_create = stock_obj.lkf_api.post_forms_answers(metadata)
    #     print('res_create', res_create)
    #     qty = self.do_test_stock(product_code, product_sku, product_lot, warehouse_to, location_to, move_qty)
    #     print('qty', qty)
    #     print('move_qty', move_qty)
    #     TestStock.stock_move_wh_1_qty = move_qty
    #     assert qty == move_qty
    #     cant_restante = TestStock.initial_move_qty - move_qty
    #     print('cant_restante', cant_restante)
    #     qty = self.do_test_stock(product_code, product_sku, product_lot, warehouse_from, location_from, cant_restante )
    #     print(f'Quedan en {warehouse_from} qty', qty)
    #     assert qty  == cant_restante