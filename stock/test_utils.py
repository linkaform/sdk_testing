# -*- coding: utf-8 -*-
import sys, simplejson, copy, time, random, string
from datetime import datetime ,timedelta


from lkf_modules.stock.items.scripts.Stock.stock_utils import Stock

from account_settings import *


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

 
class TestStock:

    supplier_warehouse = 'Proveedores'
    supplier_wh_location = 'CONDUMEX'

    stock_warehouse_1 = 'Almacen Auxiliar'
    stock_warehouse_location_1 = 'Monterrey'

    stock_warehouse_to = 'Victor Lopez'
    stock_warehouse_location_to = 'Almacen Cobre'

    product_lot =  None
    product_code = "1000887"
    product_sku = "R1000887"
    product_name = "VALVULA DE PRUEBA"
    initial_move_qty = 1000

    product_code_2 = "137580"
    product_sku_2 = "F137580"
    # product_lot_2 = "Lote 1"
    product_name_2 = "Fibra Condumex, Fibra Fiber Home, Fibra Huawei, Fibra ZTE"
    initial_move_qty_2 = 2000

    ont_code = "1468270"
    ont_sku = "F1468270"
    ont_name = "ONT FIBRA"

    #initial_move_qty = 5

    def do_test_stock(self, product_code, sku, lot_number, warehouse, location, qty, extra_qty=0, sleep=True):
        qty = self.get_test_stock_qty(product_code, sku, lot_number, warehouse, location, qty, extra_qty, sleep=sleep)
        catalog_records = self.get_test_stock_qty_catalog(product_code, lot_number, warehouse, location)
        if not catalog_records:
            time.sleep(2)
            catalog_records = self.get_test_stock_qty_catalog(product_code, lot_number, warehouse, location)
        catalog_records_qty = 0
        for rec in catalog_records:
            catalog_records_qty = rec.get(stock_obj.f['actuals'])
        assert qty == catalog_records_qty
        return qty

    def create_warehouse(self, warehouse_name):
        print('create warehouse')
        print('TODO CREAR WAREHOUSE Y SI EXISTE REGRESAR NOMBRE')
        return warehouse_name

    def create_warehouse_location(self, location_name):
        print('create_warehouse_location')
        print('TODO CREAR LOCATION Y SI EXISTE REGRESAR NOMBRE')
        return location_name

    def get_warehouses(self):
        warehouse_from = self.create_warehouse('Proveedores')
        warehouse_from_location = self.create_warehouse_location('CONDUMEX')
        
        warehouse_in = self.create_warehouse('Almacen Auxiliar')
        warehouse_in_location = self.create_warehouse_location('Refacciones Mantenimiento')
        return warehouse_in, warehouse_in_location, warehouse_from, warehouse_from_location

    def get_product_lot(self):
        letra = random.choice(string.ascii_uppercase)
        numero = random.randint(1, 20)
        working_group = random.randint(1, 9)
        product_lot = f"{numero}{letra}-{working_group}"
        return product_lot

    def get_test_stock_qty(self, product_code, sku, lot_number, warehouse, location, qty, extra_qty=0, sleep=True):
        # sku = new_lot_rec['answers'][stock_obj.SKU_OBJ_ID][stock_obj.f['product_sku']] 
        # print('sku',sku)
        # Va a revisar el almacen de location 1
        if sleep:
            time.sleep(5)
        form_id = stock_obj.FORM_INVENTORY_ID
        stock_res_loc1 = stock_obj.get_invtory_record_by_product(form_id, product_code, sku, lot_number, warehouse, location)
        stock_res_loc1 = stock_obj.get_invtory_record_by_product(form_id, product_code, sku, lot_number, warehouse, location)
        acutalas_1 = stock_res_loc1['answers'][stock_obj.f['actuals']]
        acutalas_1 = stock_res_loc1['answers'][stock_obj.f['actuals']]
        assert acutalas_1 == int(qty+extra_qty)
        calc_actuals = stock_obj.get_product_stock(product_code, sku=sku, lot_number=lot_number, warehouse=warehouse, location=location)
        assert acutalas_1 == calc_actuals['actuals']
        # calc_actuals = stock_obj.get_product_stock(product_code, sku=None, lot_number=lot_number, warehouse=warehouse, location=location)
        return acutalas_1

    def get_test_stock_qty_catalog(self, product_code, lot_number, warehouse, location ):
        mango_query = {
            "selector":{"answers": {}},
            "limit":1000,
            "skip":0
            }
        query = {
            stock_obj.f['product_code']:product_code,
            stock_obj.f['product_lot']:lot_number,
            stock_obj.f['warehouse']:warehouse,
            stock_obj.f['warehouse_location']:location,
        }
        mango_query['selector']['answers'].update(query)
        print('mango_query=', simplejson.dumps(mango_query, indent=3))
        if False:
            #TODO gargabe collector
            mango_query['selector']['answers'].update({stock_obj.f['inventory_status']: "Done"})
        res = stock_obj.lkf_api.search_catalog( stock_obj.CATALOG_INVENTORY_ID, mango_query)
        return res

    def move_metadata(self, product_code, product_sku, product_lot, warehouse_from, location_from, warehouse_to, location_to, qty, qty2, **kwargs):
        product_code_2 = kwargs.get('product_code_2', TestStock.product_code_2)
        product_sku_2 = kwargs.get('product_sku_2', TestStock.product_sku_2)
        metadata = {
            "form_id": stock_obj.STOCK_ONE_MANY_ONE, "geolocation": [], "start_timestamp": 1715787608.475, "end_timestamp": 1715788138.316,
            "answers": {
                stock_obj.f['grading_date']: fecha_datetime,
                    ###### Catalog Select ######
                stock_obj.WH.WAREHOUSE_LOCATION_OBJ_ID:{
                    stock_obj.WH.f['warehouse']: warehouse_from,
                    stock_obj.WH.f['warehouse_location']: location_from,
                },
                stock_obj.WH.WAREHOUSE_LOCATION_DEST_OBJ_ID:{
                        stock_obj.WH.f['warehouse_dest']: warehouse_to,
                        stock_obj.WH.f['warehouse_location_dest']: location_to,
                    },
                stock_obj.f['move_group']: [{
                    stock_obj.f['inv_adjust_grp_status']: 'todo',
                    stock_obj.CATALOG_INVENTORY_OBJ_ID: {
                        stock_obj.Product.f['product_code']: product_code,
                        stock_obj.Product.f['product_sku']: product_sku,
                        stock_obj.f['product_lot']: product_lot,
                        },
                    stock_obj.f['move_group_qty']: qty
                    },
                    {
                    stock_obj.f['inv_adjust_grp_status']: 'todo',
                    stock_obj.CATALOG_INVENTORY_OBJ_ID: {
                        stock_obj.Product.f['product_code']: product_code_2,
                        stock_obj.Product.f['product_sku']: product_sku_2,
                        stock_obj.f['product_lot']: product_lot,
                        },
                    stock_obj.f['move_group_qty']: qty2 
                    }
                ],
                stock_obj.f['inv_adjust_status']: 'to_do',
                stock_obj.f['observaciones_move_stock']: 'Pruebas Unitarias Movimiento de almacen',
                stock_obj.f['evidencia_salida']: [{
                            "file_name": "ejemplo_evidnecia.pdf",
                            "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/6650c41a967ad190e6a76dd3/67ead23eaf630d6b0af9cc29.pdf"
                            }],
            },
            "properties": {"device_properties": {"system": "Testing"}}
        }
        return metadata

    def salida_ont_metadata(self, product_code, product_sku, product_lot, warehouse_from, location_from, warehouse_to, location_to, qty, qty2, **kwargs):
        product_code_2 = kwargs.get('product_code_2', TestStock.product_code_2)
        product_sku_2 = kwargs.get('product_sku_2', TestStock.product_sku_2)
        metadata = {
            "form_id": stock_obj.STOCK_ONE_MANY_ONE, "geolocation": [], "start_timestamp": 1715787608.475, "end_timestamp": 1715788138.316,
            "answers": {
                stock_obj.f['grading_date']: fecha_datetime,
                    ###### Catalog Select ######
                stock_obj.WH.WAREHOUSE_LOCATION_OBJ_ID:{
                    stock_obj.WH.f['warehouse']: warehouse_from,
                    stock_obj.WH.f['warehouse_location']: location_from,
                },
                stock_obj.WH.WAREHOUSE_LOCATION_DEST_OBJ_ID:{
                        stock_obj.WH.f['warehouse_dest']: warehouse_to,
                        stock_obj.WH.f['warehouse_location_dest']: location_to,
                    },
                stock_obj.f['move_group']: [  
                    {
                        stock_obj.CATALOG_INVENTORY_OBJ_ID: {
                            stock_obj.Product.f['product_code']: TestStock.ont_code,
                            stock_obj.Product.f['product_sku']: TestStock.ont_sku,
                            stock_obj.Product.f['product_name']: [
                                TestStock.ont_name
                            ],
                            stock_obj.Product.f['sku_percontainer']: [
                                1
                            ]
                        },
                        stock_obj.f['inv_adjust_grp_status']: "todo",
                    },
                ],
                stock_obj.f['inv_adjust_status']: 'to_do',
                stock_obj.f['observaciones_move_stock']: 'Pruebas Unitarias Salidas de ONT',
                stock_obj.mf['xls_file']: [{
                            "file_name": "ONT_test.xlsx",
                            "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/6650c41a967ad190e6a76dd3/682d4d99ed7a3bd85bd32ac9.xlsx"
                            # "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/6650c41a967ad190e6a76dd3/682d4937d352be8d89cea22c.xlsx"
                            }],
                stock_obj.f['evidencia_salida']: [{
                            "file_name": "ejemplo_evidnecia.pdf",
                            "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/6650c41a967ad190e6a76dd3/67ead23eaf630d6b0af9cc29.pdf"
                            }],
            },
            "properties": {"device_properties": {"system": "Testing"}}
        }
        return metadata

    def recibo_de_material(self, product_code, product_sku, product_name, warehouse_in, location_in, qty):
        print('entra aq test_crea_recepcion_materiales')
        supplier_warehouse = TestStock.supplier_warehouse
        supplier_wh_location = TestStock.supplier_wh_location
        # warehouse_in, warehouse_in_location, warehouse_from, warehouse_from_location = self.get_warehouses()
        TestStock.product_lot = self.get_product_lot()
        metadata = {
            "form_id": stock_obj.STOCK_IN_ONE_MANY_ONE,"geolocation": [],"start_timestamp": 1715787608.475,"end_timestamp": 1715788138.316,
            "answers": {
                stock_obj.f['grading_date']: fecha_datetime,
                stock_obj.WH.WAREHOUSE_LOCATION_OBJ_ID: {
                    stock_obj.WH.f['warehouse']: supplier_warehouse,
                    stock_obj.WH.f['warehouse_location']: supplier_wh_location
                },
                stock_obj.WH.WAREHOUSE_LOCATION_DEST_OBJ_ID: {
                    stock_obj.WH.f['warehouse_dest']: warehouse_in,
                    stock_obj.WH.f['warehouse_location_dest']: location_in
                },
                stock_obj.f['move_group']: [
                    {
                        stock_obj.Product.SKU_OBJ_ID: {
                            stock_obj.Product.f['product_code']: TestStock.product_code,
                            stock_obj.Product.f['product_sku']: TestStock.product_sku,
                            stock_obj.Product.f['product_name']: [
                                TestStock.product_name
                            ],
                            stock_obj.Product.f['sku_percontainer']: [
                                1
                            ]
                        },
                        stock_obj.f['product_lot']: TestStock.product_lot,
                        stock_obj.f['inv_adjust_grp_status']: "todo",
                        stock_obj.f['move_group_qty']: TestStock.initial_move_qty,
                    },
                    {
                        stock_obj.Product.SKU_OBJ_ID: {
                            stock_obj.Product.f['product_code']: TestStock.product_code_2,
                            stock_obj.Product.f['product_sku']: TestStock.product_sku_2,
                            stock_obj.Product.f['product_name']: [
                                TestStock.product_name_2
                            ],
                            stock_obj.Product.f['sku_percontainer']: [
                                1
                            ]
                        },
                        stock_obj.f['product_lot']: TestStock.product_lot,
                        stock_obj.f['inv_adjust_grp_status']: "todo",
                        stock_obj.f['move_group_qty']: TestStock.initial_move_qty_2,
                    },
                ],
                stock_obj.f['stock_status']: "to_do",
                stock_obj.f['stock_move_comments']: f"Comentario pruebas unitarias: {stock_obj.today_str()}",
                stock_obj.f['evidencia']: [{
                            "file_name": "ejemplo_evidnecia.pdf",
                            "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/6650c41a967ad190e6a76dd3/67ead23eaf630d6b0af9cc29.pdf"
                            }],
            },
            "folio":None, 
            "properties":{ "device_properties":{"system":"Testing"} }
        }
        return metadata
    
    def recibo_de_ont(self, product_code, product_sku, product_name, warehouse_in, location_in, qty):
        print('entra aq test_crea_recepcion_materiales')
        supplier_warehouse = TestStock.supplier_warehouse
        supplier_wh_location = TestStock.supplier_wh_location
        # warehouse_in, warehouse_in_location, warehouse_from, warehouse_from_location = self.get_warehouses()
        metadata = {
            "form_id": stock_obj.STOCK_IN_ONE_MANY_ONE,"geolocation": [],"start_timestamp": 1715787608.475,"end_timestamp": 1715788138.316,
            "answers": {
                stock_obj.f['grading_date']: fecha_datetime,
                stock_obj.WH.WAREHOUSE_LOCATION_OBJ_ID: {
                    stock_obj.WH.f['warehouse']: supplier_warehouse,
                    stock_obj.WH.f['warehouse_location']: supplier_wh_location
                },
                stock_obj.WH.WAREHOUSE_LOCATION_DEST_OBJ_ID: {
                    stock_obj.WH.f['warehouse_dest']: warehouse_in,
                    stock_obj.WH.f['warehouse_location_dest']: location_in
                },
                stock_obj.f['move_group']: [
                    {
                        stock_obj.Product.SKU_OBJ_ID: {
                            stock_obj.Product.f['product_code']: TestStock.ont_code,
                            stock_obj.Product.f['product_sku']: TestStock.ont_sku,
                            stock_obj.Product.f['product_name']: [
                                TestStock.ont_name
                            ],
                            stock_obj.Product.f['sku_percontainer']: [
                                1
                            ]
                        },
                        stock_obj.f['inv_adjust_grp_status']: "todo",
                    },
                ],
                stock_obj.f['stock_status']: "to_do",
                stock_obj.f['stock_move_comments']: f"Comentario pruebas unitarias: {stock_obj.today_str()}",
                stock_obj.mf['xls_file']: [{
                            "file_name": "ONT_test.xlsx",
                            "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/6650c41a967ad190e6a76dd3/682d4d99ed7a3bd85bd32ac9.xlsx"
                            # "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/6650c41a967ad190e6a76dd3/682d4937d352be8d89cea22c.xlsx"
                            }],
                stock_obj.f['evidencia']: [{
                            "file_name": "ejemplo_evidnecia.pdf",
                            "file_url": "https://f001.backblazeb2.com/file/app-linkaform/public-client-126/71202/6650c41a967ad190e6a76dd3/67ead23eaf630d6b0af9cc29.pdf"
                            }],
            },
            "folio":None, 
            "properties":{ "device_properties":{"system":"Testing"} }
        }
        return metadata        

print('se pasooooooooooo-------')