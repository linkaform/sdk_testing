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
    supplier_wh_location = 'Proveedor de Piezas'

    stock_warehouse_1 = 'Almacen Central'
    stock_warehouse_location_1 = 'Bodega Producto Terminado'

    product_lot =  None

    product_code = "TS-001"
    product_sku = "TS-001-CH"
    product_name = "Camisa Modelo 1"
    initial_move_qty = 1000


    product_code_2 = "MM-C14"
    product_sku_2 = "MM-C14-10M"
    product_name_2 = "Manguera 1/4"
    initial_move_qty_2 = 2000


    def do_test_stock(self, product_code, sku, lot_number, warehouse, location, qty, extra_qty=0, sleep=True):
        print('do_test_stock qty=',qty)
        qty = self.get_test_stock_qty(product_code, sku, lot_number, warehouse, location, qty, extra_qty, sleep=sleep)
        print('2222do_test_stock qty=',qty)
        catalog_records = self.get_test_stock_qty_catalog(product_code, lot_number, warehouse, location)
        print('catalog_records qty=',catalog_records)
        if not catalog_records:
            time.sleep(2)
            catalog_records = self.get_test_stock_qty_catalog(product_code, lot_number, warehouse, location)
            print('catalog_records qty222=',catalog_records)
        catalog_records_qty = 0
        for rec in catalog_records:
            print('qty1_catalog',rec.get(stock_obj.f['actuals']))
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

        print('stock_res_loc1', stock_res_loc1)
        print('form_id', form_id)
        print('product_code', product_code)
        print('sku', sku)
        print('lot_number', lot_number)
        print('warehouse', warehouse)
        print('location', location)
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

    def move_metadata(self, warehouse_from, location_from, warehouse_to, location_to ):
        qty = 100
        qty2 = 200
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
                        stock_obj.Product.f['product_code']: TestStock.product_code,
                        stock_obj.Product.f['product_sku']: TestStock.product_sku,
                        stock_obj.f['product_lot']: TestStock.product_lot,
                        },
                    stock_obj.f['move_group_qty']: qty,
                    },
                    {
                    stock_obj.CATALOG_INVENTORY_OBJ_ID: {
                        stock_obj.Product.f['product_code']: TestStock.product_code_2,
                        stock_obj.Product.f['product_sku']: TestStock.product_sku_2,
                        stock_obj.f['product_lot']: TestStock.product_lot,
                        },
                    stock_obj.f['move_group_qty']: qty2,
                    }
                    ],
                stock_obj.f['inv_adjust_status']: 'to_do',
            },
            "properties": {"device_properties": {"system": "Testing"}}
        }
        return metadata

    def recibo_de_material(self, warehouse_in, location_in):
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
                    }
                ],
                stock_obj.f['stock_status']: "to_do",
                stock_obj.f['stock_move_comments']: f"Comentario pruebas unitarias: {stock_obj.today_str()}",
            },
            "folio":None, 
            "properties":{ "device_properties":{"system":"Testing"} }
        }

        # print('metadata', simplejson.dumps(metadata, indent=3))
        return metadata
        

    # def test_create_inventory_adjustment(self):
    #     metadata = {
    #         "form_id": FORM_INVENTORY_ADJUSTMENT,"geolocation": [],"start_timestamp": 1715787608.475,"end_timestamp": 1715788138.316,
    #         "answers": {
    #             "6442e4537775ce64ef72dd6a": "todo",
    #             CATALOG_WAREHOUSE_LOCATION_OBJ_ID: {
    #                 "6442e4831198daf81456f274": "Almacen Central",
    #                 "65ac6fbc070b93e656bd7fbe": "Refacciones Mantenimiento"
    #             },
    #             "644bf7ccfa9830903f087867": [
    #                 {
    #                     CATALOG_SKU_OBJ_ID: {
    #                         "61ef32bcdf0ec2ba73dec33d": "MM-C14",
    #                         "65dec64a3199f9a040829243": "MM-C14-10M",
    #                         "61ef32bcdf0ec2ba73dec33e": [
    #                             "Manguera 1/4"
    #                         ],
    #                         "6205f73281bb36a6f1573358": [
    #                             "S1"
    #                         ],
    #                         "621fca56ee94313e8d8c5e2e": [
    #                             "Negro"
    #                         ]
    #                     },
    #                     "ad00000000000000000ad999": "todo",
    #                     "620a9ee0a449b98114f61d77": "L1",
    #                     "ad00000000000000000ad000": 20,
    #                     "ad00000000000000000ad100": 20
    #                 }
    #             ],
    #             "000000000000000000000111": f"{fecha} 21:29:30"
    #         },
    #         "folio":None,"properties":{ "device_properties":{"system":"Testing"} }
    #     }
    #     res_create =  lkf_api.post_forms_answers(metadata)
    #     print('res_create',res_create)
    #     assert res_create['status_code'] == 201
    #     time.sleep(15)

    # def test_create_salida_multi_a_una_ubicacion(self):
    #     metadata = {
    #         "form_id": FORM_MOVE_ONE_MANY_ONE,"geolocation": [],"start_timestamp": 1715787608.475,"end_timestamp": 1715788138.316,
    #         "answers": {
    #             CATALOG_WAREHOUSE_LOCATION_OBJ_ID: {
    #                 "6442e4831198daf81456f274": "Almacen Central",
    #                 "65ac6fbc070b93e656bd7fbe": "Refacciones Mantenimiento"
    #             },
    #             CATALOG_WAREHOUSE_LOCATION_DEST_OBJ_ID: {
    #                 "65bdc71b3e183f49761a33b9": "Produccion",
    #                 "65c12749cfed7d3a0e1a341b": "Maquina Blanca"
    #             },
    #             "6442e4537775ce64ef72dd69": [
    #                 {
    #                     CATALOG_STOCK_INVENTORY_OBJ_ID: {
    #                         "61ef32bcdf0ec2ba73dec33d": "MM-C14",
    #                         "65dec64a3199f9a040829243": "MM-C14-10M",
    #                         "620a9ee0a449b98114f61d77": "L1",
    #                         "61ef32bcdf0ec2ba73dec33e": [
    #                             "Manguera 1/4"
    #                         ],
    #                         "6441d33a153b3521f5b2afc9": [
    #                             20
    #                         ],
    #                         "621fca56ee94313e8d8c5e2e": [],
    #                         "621fc992a7ebfd603a8c5e2e": [],
    #                         "6205f73281bb36a6f1573358": [],
    #                         "61ef32bcdf0ec2ba73dec342": [],
    #                         "6205f73281bb36a6f157335b": [
    #                             1
    #                         ],
    #                         "6209705080c17c97320e3382": [],
    #                         "61ef32bcdf0ec2ba73dec343": []
    #                     },
    #                     "65e1169689c0e0790f8843f1": 5,
    #                     "6442e4cc45983bf1778ec17d": 5
    #                 }
    #             ],
    #             "000000000000000000000111": fecha_salida,
    #             "6442e4537775ce64ef72dd6a": "to_do"
    #         },
    #         "folio":None,"properties":{ "device_properties":{"system":"Testing"} }
    #     }
    #     res_create =  lkf_api.post_forms_answers(metadata)
    #     print('res_create',res_create)
    #     assert res_create['status_code'] == 201
    #     time.sleep(15)

print('se pasooooooooooo-------')