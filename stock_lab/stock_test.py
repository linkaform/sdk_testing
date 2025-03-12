# -*- coding: utf-8 -*-
import sys, simplejson, copy, time, random, string, math, json
from datetime import datetime ,timedelta

from lkf_modules.stock_lab.items.scripts.Lab.lab_stock_utils import Stock
from lkf_addons.addons.stock_greenhouse.app import Stock as Stock_greenhouse

from account_settings import *
# from stock_functions import *


print('starting test')
stock_obj = Stock(settings, use_api=True)
stock_obj_greenhouse = Stock_greenhouse(settings, use_api=True)

stock_obj.load(module='Product', **stock_obj.kwargs)
stock_obj.load(module='Product', module_class='Warehouse', import_as='WH', **stock_obj.kwargs)
stock_obj.load(module='Employee', **stock_obj.kwargs)

fecha = datetime.now()
prod_year = fecha.isocalendar().year
prod_week = fecha.isocalendar().week
ready_yr_wk = int(str(fecha.isocalendar().year) + str(fecha.isocalendar().week))
fecha_salida = fecha + timedelta(days=1)
fecha_str = fecha.strftime('%Y-%m-%d')
fecha_datetime = fecha.strftime('%Y-%m-%d %H:%M:%S')
cut_day = fecha.strftime('%j')
fecha_salida = fecha_salida.strftime('%Y-%m-%d')
hours_in = '10:00:00'
hours_out = '11:00:00'

product_code_1 = 'LNAFP'
product_name_1 = 'Nandina domestica nana Firepower'
product_stage_1 = 'S2'
product_stage_3 = 'S3'
product_stage_4 = 'Ln72'
product_department = 'LAB'

product_code_2 = 'LAGBG'
product_name_2 = 'Blue Glow Agave'


letra1 = random.choice(string.ascii_uppercase)
numero1 = random.randint(1, 9)

letra2 = random.choice(string.ascii_uppercase)
numero2 = random.randint(1, 9)

working_group_1 = random.randint(1, 9)
working_cycle_1 = f"{letra1}{numero1}"
working_group_2 = random.randint(1, 9)
working_cycle_2 = f"{letra2}{numero2}"


class TestStock:

    lot_number = None
    prod_folio_1 = None
    prod_id_1 = None
    total_produced_1 = 0
    stock_location_1_qty = 0
    stock_location_2_qty = 0
    stock_location_3_qty = 0
    stock2_location_1_qty = 0
    stock2_location_2_qty = 0
    stock_lote1_qty = 0
    stock_lote2_qty = 0
    prod_folio_2 = None
    prod_id_2 = None
    total_produced_2 = 0
    prod_folio_3 = None
    prod_id_3 = None
    total_produced_3 = 0
    stock_move_location_1_qty = 0



    def adjust_metadata(self, product_code, product_stage, media_tray, per_container, warehouse, location, qty):
        print('prod_week', prod_week)
        metadata = {
            "form_id": stock_obj.ADJUIST_FORM_ID, "geolocation": [], "start_timestamp": 1715787608.475, "end_timestamp": 1715788138.316,
            "answers": {
                stock_obj.f['grading_date']: fecha_datetime,
                stock_obj.WH.WAREHOUSE_LOCATION_OBJ_ID:{
                        stock_obj.WH.f['warehouse']: warehouse,
                        stock_obj.WH.f['warehouse_location']: location,
                    },
                stock_obj.f['grading_group'] : [
                    {
                    stock_obj.Product.PRODUCT_RECIPE_OBJ_ID:{
                        stock_obj.Product.f['product_code']: product_code,
                        stock_obj.f['reicpe_stage']: product_stage,
                        stock_obj.f['reicpe_container']: media_tray,
                        stock_obj.f['reicpe_per_container']: per_container,
                        },
                        stock_obj.f['plant_cut_year']: prod_year,
                        # stock_obj.f['plant_cut_day']: ,
                        #TODO aqui esta poniendo mal el prod week por el tema de las semanas
                        stock_obj.f['production_cut_week']:str(int(prod_week) - 1)  ,
                        stock_obj.f['plant_cycle']: TestStock.working_cycle ,
                        stock_obj.f['adjust_lot_by']: 'week',
                        stock_obj.f['plant_group']: TestStock.working_group,
                        stock_obj.f['plant_contamin_code']: 'white',
                        stock_obj.f['inv_adjust_grp_qty']: qty ,
                        # stock_obj.f['inv_adjust_grp_out']: ,
                        # stock_obj.f['inv_adjust_grp_in']: ,
                        stock_obj.f['inv_adjust_grp_status']: 'todo' ,
                        stock_obj.f['inv_adjust_grp_comments']: 'comment...',
                    }
                ],
                stock_obj.f['inv_adjust_comments'] : 'One set',
                stock_obj.f['inv_adjust_status'] : 'todo'
            },
            "properties": {"device_properties": {"system": "Testing"}}
        }
        return metadata

    def do_move_stock_in(self, prod_folio, warehouse, location, location_2, total_produced):
        mongo_query = {
            "form_id" : stock_obj.MOVE_NEW_PRODUCTION_ID,
            f"answers.{stock_obj.f['production_folio']}": prod_folio
        }
        #se obtiene registro con query de folio de prudccion
        print('mongo_query', mongo_query)
        new_lot_rec = stock_obj.cr.find(mongo_query)
        new_lot_rec = new_lot_rec.next()
        TestStock.new_lot_id = new_lot_rec.get('_id')
        TestStock.new_lot_folio = new_lot_rec.get('folio')
        # se selecciona almacen destino y location
        warehouse = self.create_warehouse(warehouse)
        location = self.create_warehouse_location(location)
        # se arma el set de movimiento
        stock_location_1_qty = int(random.random() * 100)
        new_location = {
            stock_obj.WH.WAREHOUSE_DEST_OBJ_ID: {
                stock_obj.WH.f['warehouse'] : warehouse,
                stock_obj.WH.f['warehouse_location']: location

            },
            stock_obj.f['new_location_racks']: 0 ,
            stock_obj.f['new_location_containers']: stock_location_1_qty
        }
        # se pon dentro de la variable grupo el set1
        new_location_group = [new_location]
        # se anexa al registro completo el grupo
        new_lot_rec['answers'][stock_obj.f['new_location_group']] = new_location_group

        # se edita el registr y se verifica que regrese un 400 debido a mala cantidad
        res = stock_obj.lkf_api.patch_record(new_lot_rec, new_lot_rec['_id'])
        assert res['status_code'] == 400
        location_2 = self.create_warehouse_location(location_2)
        # se prepara set 2
        stock_location_2_qty = total_produced  - stock_location_1_qty 
        new_location_2 = {
            stock_obj.WH.WAREHOUSE_DEST_OBJ_ID: {
                stock_obj.WH.f['warehouse'] : warehouse,
                stock_obj.WH.f['warehouse_location']: location_2
            },
            stock_obj.f['new_location_racks']: 0 ,
            stock_obj.f['new_location_containers']: stock_location_2_qty
        }
        # se se anexa al grupo
        new_location_group.append(new_location_2)

        # se acutaliza el registro y se hace patch
        new_lot_rec['answers'][stock_obj.f['new_location_group']] = new_location_group

        res = stock_obj.lkf_api.patch_record(new_lot_rec, TestStock.new_lot_id )
        print('sleeping...... 4s')
        time.sleep(4)
        print('res=',res)
        assert res['status_code'] == 202
        product_code = new_lot_rec['answers'][stock_obj.SKU_OBJ_ID][stock_obj.f['product_code']] 
        lot_number = new_lot_rec['answers'][stock_obj.f['product_lot']] 
        # self.get_test_stock_qty(product_code_1, lot_number_1, warehouse, warehouse_in_location_1, stock_location_1 )
        assert stock_location_2_qty + stock_location_1_qty == int(total_produced)
        TestStock.product_code = product_code
        TestStock.lot_number = lot_number
        return stock_location_1_qty, stock_location_2_qty
    
    def do_move_stock_in_greenhouse(self, prod_folio, warehouse, location, location_2, total_produced):
        mongo_query = {
            "form_id" : stock_obj_greenhouse.STOCK_MOVE_FORM_ID #no folio
        }
        #se obtiene registro con query de folio de prudccion
        print('mongo_query', mongo_query)
        new_lot_rec = stock_obj_greenhouse.cr.find(mongo_query)
        new_lot_rec = new_lot_rec.next()
        print('+++new_lot_rec', new_lot_rec)
        TestStock.new_lot_id = new_lot_rec.get('_id')
        TestStock.new_lot_folio = new_lot_rec.get('folio')
        # se selecciona almacen destino y location
        warehouse = self.create_warehouse(warehouse)
        location = self.create_warehouse_location(location)
        # se arma el set de movimiento
        stock_location_1_qty = int(random.random() * 100)
        new_location = {
            stock_obj.WH.WAREHOUSE_DEST_OBJ_ID: {
                stock_obj.WH.f['warehouse'] : warehouse,
                stock_obj.WH.f['warehouse_location']: location

            },
            stock_obj.f['new_location_racks']: 0 ,
            stock_obj.f['new_location_containers']: stock_location_1_qty
        }
        # se pon dentro de la variable grupo el set1
        new_location_group = [new_location]
        # se anexa al registro completo el grupo
        new_lot_rec['answers'][stock_obj.f['new_location_group']] = new_location_group
        print('new_lot_rec', new_lot_rec)

        # se edita el registr y se verifica que regrese un 400 debido a mala cantidad
        res = stock_obj.lkf_api.patch_record(new_lot_rec, new_lot_rec['_id'])
        print ('res', res)
        assert res['status_code'] == 200
        location_2 = self.create_warehouse_location(location_2)
        # se prepara set 2
        stock_location_2_qty = total_produced  - stock_location_1_qty 
        new_location_2 = {
            stock_obj.WH.WAREHOUSE_DEST_OBJ_ID: {
                stock_obj.WH.f['warehouse'] : warehouse,
                stock_obj.WH.f['warehouse_location']: location_2
            },
            stock_obj.f['new_location_racks']: 0 ,
            stock_obj.f['new_location_containers']: stock_location_2_qty
        }
        # se se anexa al grupo
        new_location_group.append(new_location_2)

        # se acutaliza el registro y se hace patch
        new_lot_rec['answers'][stock_obj.f['new_location_group']] = new_location_group

        res = stock_obj.lkf_api.patch_record(new_lot_rec, TestStock.new_lot_id )
        print('sleeping...... 4s')
        time.sleep(4)
        print('res=',res)
        assert res['status_code'] == 200
        #product_code = new_lot_rec['answers'][stock_obj.SKU_OBJ_ID][stock_obj.f['product_code']] 
        #lot_number = new_lot_rec['answers'][stock_obj.f['product_lot']] 
        # self.get_test_stock_qty(product_code_1, lot_number_1, warehouse, warehouse_in_location_1, stock_location_1 )
        assert stock_location_2_qty + stock_location_1_qty == int(total_produced)
        # TestStock.product_code = product_code
        #TestStock.lot_number = lot_number
        return stock_location_1_qty, stock_location_2_qty    
       
    def do_test_stock(self, product_code, lot_number, warehouse, location, qty, extra_qty=0):
        print('do_test_stock qty=',qty)
        qty = self.get_test_stock_qty(product_code, lot_number, warehouse, location, qty, extra_qty)
        catalog_records = self.get_test_stock_qty_catalog(product_code, lot_number, warehouse, location)
        for rec in catalog_records:
            print('qty1_catalog',rec.get(stock_obj.f['actuals']))
            catalog_records_qty = rec.get(stock_obj.f['actuals'])
            assert qty == catalog_records_qty
        return qty

        # qty1 = self.get_test_stock_qty(product_code, lot_number, warehouse, location, stock_location_1_qty)
        # qty2 = self.get_test_stock_qty(product_code, lot_number, warehouse, location_2, stock_location_2_qty)
        # assert qty1 + qty2 == int(total_produced)
        # catalog_records_2 = self.get_test_stock_qty_catalog(product_code, lot_number, warehouse, location_2)
        # print('catalog_records',catalog_records)
        # for rec in catalog_records:
        #     print('qty1_catalog',rec.get(stock_obj.f['actuals']))
        #     catalog_qty1 = rec.get(stock_obj.f['actuals'])
        #     assert qty1 == catalog_qty1
        # for rec in catalog_records_2:
        #     print('qty1_catalog',rec.get(stock_obj.f['actuals']))
        #     catalog_qty2 = rec.get(stock_obj.f['actuals'])
        #     assert qty2 == catalog_qty2

    def create_warehouse(self, warehouse_name):
        print('create warehouse')
        print('TODO CREAR WAREHOUSE Y SI EXISTE REGRESAR NOMBRE')
        return warehouse_name

    def create_warehouse_location(self, location_name):
        print('create_warehouse_location')
        print('TODO CREAR LOCATION Y SI EXISTE REGRESAR NOMBRE')
        return location_name

    def get_group_cyle(self):
        letra = random.choice(string.ascii_uppercase)
        numero = random.randint(1, 9)
        working_group = random.randint(1, 9)
        working_cycle = f"{letra}{numero}"
        return working_group, working_cycle

    def get_test_stock_qty(self, product_code, lot_number, warehouse, location, qty, extra_qty=0):
        # sku = new_lot_rec['answers'][stock_obj.SKU_OBJ_ID][stock_obj.f['product_sku']] 
        # print('sku',sku)
        # Va a revisar el almacen de location 1
        print('get_test_stock_qty qty',qty)
        print('extra_qty qty',extra_qty)
        print('product_code',product_code)
        print('lot_number',lot_number)
        print('warehouse',warehouse)
        print('location',location)
        time.sleep(5)
        stock_res_loc1 = stock_obj.get_invtory_record_by_product(stock_obj.FORM_INVENTORY_ID, product_code, lot_number, warehouse, location)
        print('stock_res_loc1',stock_res_loc1)
        print('actualsactuals',stock_obj.f['actuals'])
        acutalas_1 = stock_res_loc1['answers'][stock_obj.f['actuals']]
        print('acutalas_1',acutalas_1)
        assert acutalas_1 == int(qty+extra_qty)
        calc_actuals = stock_obj.get_product_stock(product_code, sku=None, lot_number=lot_number, warehouse=warehouse, location=location)
        print('calc_actuals',calc_actuals)
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
        print('mango_query=', mango_query)
        if False:
            #TODO gargabe collector
            mango_query['selector']['answers'].update({stock_obj.f['inventory_status']: "Done"})
        res = stock_obj.lkf_api.search_catalog( stock_obj.CATALOG_INVENTORY_ID, mango_query)
        return res

    def get_warehouses(self):
        warehouse_from = self.create_warehouse('Proveedores')
        warehouse_from_location = self.create_warehouse_location('CONDUMEX')
        
        warehouse_in = self.create_warehouse('Almacen Auxiliar')
        warehouse_in_location = self.create_warehouse_location('Refacciones Mantenimiento')
        return warehouse_in, warehouse_in_location, warehouse_from, warehouse_from_location

    def move_metadata(self, product_code, product_lot, warehouse_from, location_from, warehouse_to, location_to, qty):
        metadata = {
            "form_id": stock_obj.STOCK_MOVE_FORM_ID, "geolocation": [], "start_timestamp": 1715787608.475, "end_timestamp": 1715788138.316,
            "answers": {
                stock_obj.f['grading_date']: fecha_datetime,
                stock_obj.CATALOG_INVENTORY_OBJ_ID: {
                    ###### Catalog Select ######
                    stock_obj.WH.f['warehouse']: warehouse_from,
                    stock_obj.WH.f['warehouse_location']: location_from,
                    # From Stage
                    stock_obj.Product.f['product_code']: product_code,
                    stock_obj.f['plant_cut_day']: cut_day,
                    stock_obj.f['product_lot']: product_lot,  # To Stage
                },
                stock_obj.f['inv_move_qty']: qty,
                stock_obj.f['move_group']: [{
                    stock_obj.WH.WAREHOUSE_LOCATION_DEST_OBJ_ID:{
                        stock_obj.WH.f['warehouse_dest']: warehouse_to,
                        stock_obj.WH.f['warehouse_location_dest']: location_to,
                    },
                    stock_obj.f['move_group_qty']: qty,
                    }],
                stock_obj.f['inv_adjust_status']: 'to_do'
            },
            "properties": {"device_properties": {"system": "Testing"}}
        }
        return metadata

    def production_answers(self, working_group, working_cycle, qty_factor):
        prod_answers = {
            stock_obj.f['production_per_container_in']: 10,
            stock_obj.f['product_container_type']: 'clean',
            stock_obj.f['production_working_cycle']: working_cycle,
            stock_obj.f['production_working_group']: working_group,
            stock_obj.MEDIA_LOT_OBJ_ID: {
                stock_obj.f['media_name']: 'AG II',
                stock_obj.f['media_lot']: '207 A',
            },
            stock_obj.f['use_clorox']: 'no',
            stock_obj.f['production_group']: [
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID: {stock_obj.Employee.f['worker_name']: "Elizabeth Guevara"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: qty_factor * 10,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['set_production_date_out']: fecha_str,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['set_lunch_brake']: 'no',
                    stock_obj.f['production_status']: 'progress',
                },
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID: {stock_obj.Employee.f['worker_name']: "Blanca Guevara"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: qty_factor * 100,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['set_production_date_out']: fecha_str,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['set_lunch_brake']: 'no',
                    stock_obj.f['production_status']: 'progress',
                },
                {
                    stock_obj.Employee.EMPLOYEE_OBJ_ID: {stock_obj.Employee.f['worker_name']: "Anayeli Bautista"},
                    stock_obj.f['production_containers_in']: 50,
                    stock_obj.f['set_total_produced']: qty_factor * 1000,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['set_production_date_out']: fecha_str,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['set_lunch_brake']: 'no',
                    stock_obj.f['production_status']: 'progress',
                }
            ],
        }
        return prod_answers

    def production_metadata(self, product_code, product_name):
        form_stage = 'S2'
        to_stage = 'S2'
        recipe_type = 'Main'
        growth_weeks = '8'
        sku_package = 'Baby Jar'
        per_container = '10'
        reicpe_soil_type = 'NII'
        print('entra aq test_crea_recepcion_materiales')
        warehouse_in, warehouse_in_location, warehouse_from, warehouse_from_location = self.get_warehouses()
        metadata = {
            "form_id": stock_obj.PRODUCTION_FORM_ID, "geolocation": [], "start_timestamp": 1715787608.475, "end_timestamp": 1715788138.316,
            "answers": {
                stock_obj.f['production_year']: prod_year,
                stock_obj.f['production_week']: prod_week,
                stock_obj.Product.SKU_OBJ_ID: {
                    ###### Catalog Select ######
                    stock_obj.Product.f['product_code']: product_code,
                    # From Stage
                    stock_obj.Product.f['sku_color']: form_stage,
                    stock_obj.Product.f['sku_size']: to_stage,  # To Stage
                    stock_obj.f['recipe_type']: recipe_type,  # Recipe Type
                    # Grow Weeks
                    stock_obj.f['reicpe_growth_weeks']: growth_weeks,
                    stock_obj.Product.f['sku_package']: sku_package,
                    stock_obj.Product.f['sku_percontainer']: per_container,
                    ###### Catalog Details ######
                    stock_obj.Product.f['product_name']: [product_name,],
                    # Grow Weeks
                    stock_obj.f['reicpe_soil_type']: [reicpe_soil_type,],
                    stock_obj.Product.f['product_department']: [
                        product_department,]
                },
                stock_obj.f['production_requier_containers']: 80,
                stock_obj.Employee.TEAM_OBJ_ID: {stock_obj.Employee.f['team_name']: 'Team 1'},
                stock_obj.WH.WAREHOUSE_OBJ_ID: {stock_obj.WH.f['warehouse']: 'Team 1'},
                stock_obj.f['production_left_overs']: 'next_day',
                stock_obj.f['production_order_status']: 'programed',
            },
            "folio": None,
            "properties": {"device_properties": {"system": "Testing"}}
        }
        return metadata
    
    def production_metadata_greenhouse(self, product_code, product_name, total_produced):
        priority = 9
        form_stage = 'Ln72'
        to_stage = 'Ln72'
        recipe_type = 'Main'
        growth_weeks = '8'
        sku_package = 'Baby Jar'
        per_container = '72'
        reicpe_soil_type = 'CUSTOM BLEND'
        print('entra aq test_crea_recepcion_materiales')
        warehouse_in, warehouse_in_location, warehouse_from, warehouse_from_location = self.get_warehouses()
        metadata = {
            "form_id": stock_obj_greenhouse.PRODUCTION_FORM_ID, "geolocation": [], "start_timestamp": 1715787608.475, "end_timestamp": 1715788138.316,
            "answers": {
                stock_obj.f['production_year']: prod_year,
                stock_obj.f['production_week']: prod_week,
                #stock_obj.f['priority']: priority,
                ###### Catalog Select ######
                stock_obj.Product.SKU_OBJ_ID: {
                    stock_obj.f['product_code']: product_code,
                    stock_obj.f['reicpe_start_size'] : to_stage,  # To Stage
                    stock_obj.f['prod_qty_per_container']: [per_container] ,
                },
                stock_obj.f['production_lote']: ready_yr_wk,
                stock_obj.f['production_requier_containers']: 5000,
                stock_obj.f['requierd_qty_flats']: 70,
                stock_obj.f['production_group']: [{
                    stock_obj.f['product_lot_location']: 2,
                    stock_obj.f['worker_obj_id']: {
                        stock_obj.f['worker_name']: "Alexia Piche",
                    },
                    stock_obj.f['set_total_produced']: 200,
                    stock_obj.f['set_production_date']: fecha_str,
                    stock_obj.f['time_in']: hours_in,
                    stock_obj.f['time_out']: hours_out,
                    stock_obj.f['production_status']: 'progress',
                    }],
                stock_obj.f['total_produced']: total_produced,
                stock_obj.f['production_left_overs']: 'next_day',
                stock_obj.f['production_order_status']: 'programed',
            },
            "folio": None,
            "properties": {"device_properties": {"system": "Testing"}}
        }
        return metadata
    
    def pull_out_metadata(self, product_code, product_name, product_lot, product_stage, warehouse_from, location_from, warehouse_to, location_to, qty):
        print('prod_week', prod_week)
        metadata = {
            "form_id": stock_obj.STOCK_MANY_LOCATION_OUT, "geolocation": [], "start_timestamp": 1715787608.475, "end_timestamp": 1715788138.316,
            "answers": {
                stock_obj.f['grading_date']: fecha_datetime,
                stock_obj.CATALOG_PRODUCT_RECIPE_OBJ_ID:{
                    stock_obj.Product.f['product_code']: product_code,
                    stock_obj.Product.f['product_name']: [product_name,]
                },
                stock_obj.f['requierd_eaches']: 10,
                stock_obj.f['move_group']: [
                    {stock_obj.CATALOG_INVENTORY_OBJ_ID:{
                        stock_obj.f['recipe_stage']: product_stage,
                        stock_obj.f['plant_cut_day']: cut_day,
                        stock_obj.WH.f['warehouse']: warehouse_from,
                        stock_obj.WH.f['warehouse_location']: location_from,
                        stock_obj.f['product_lot']: product_lot,
                        },
                    stock_obj.f['new_location_containers']: qty,
                    }
                ],
                stock_obj.WH.WAREHOUSE_LOCATION_DEST_OBJ_ID:{
                        stock_obj.WH.f['warehouse_dest']: warehouse_to,
                        stock_obj.WH.f['warehouse_location_dest']: location_to,
                    },
                stock_obj.f['inv_adjust_status']: 'to_do',
            },
            "properties": {"device_properties": {"system": "Testing"}}
        }
        return metadata

    def revisa_producto_en_almance(self, product_code, lot_number, warehouse, location):
        # Va a revisar el almacen de location 1
        stock_res_loc1 = stock_obj.get_invtory_record_by_product(stock_obj.FORM_INVENTORY_ID, product_code, lot_number, warehouse, location)
        print('stock_res',stock_res)
        acutalas_1 = stock_res_loc1['answers'][stock_obj.f['actuals']]
        assert acutalas_1 == int(stock_location_1)

    def seleccion_planta_metadata(self, product_code, product_name, product_lot, product_stage, warehouse_from, location_from, warehouse_to, location_to, qty):
        print('prod_week', prod_week)
        metadata = {
            "form_id": stock_obj.STOCK_MANY_LOCATION_2_ONE, "geolocation": [], "start_timestamp": 1715787608.475, "end_timestamp": 1715788138.316,
            "answers": {
                stock_obj.f['grading_date']: fecha_datetime,
                stock_obj.CATALOG_PRODUCT_RECIPE_OBJ_ID:{
                    stock_obj.Product.f['product_code']: product_code,
                    stock_obj.Product.f['product_name']: [product_name,]
                },
                stock_obj.f['requierd_eaches']: 10,
                stock_obj.f['move_group']: [
                    {stock_obj.CATALOG_INVENTORY_OBJ_ID:{
                        stock_obj.f['recipe_stage']: product_stage,
                        stock_obj.f['plant_cut_day']: cut_day,
                        stock_obj.WH.f['warehouse']: warehouse_from,
                        stock_obj.WH.f['warehouse_location']: location_from,
                        stock_obj.f['product_lot']: product_lot,
                        },
                    stock_obj.f['new_location_containers']: qty,
                    }
                ],
                stock_obj.WH.WAREHOUSE_LOCATION_DEST_OBJ_ID:{
                        stock_obj.WH.f['warehouse_dest']: warehouse_to,
                        stock_obj.WH.f['warehouse_location_dest']: location_to,
                    },
                stock_obj.f['inv_adjust_status']: 'to_do',
            },
            "properties": {"device_properties": {"system": "Testing"}}
        }
        return metadata
    ##### Tests ######

    def test_production(self):
        qty_factor = 1
        product_code = 'LNAFP'
        product_name = 'Nandina domestica nana Firepower'
        product_department = 'LAB'
        metadata = self.production_metadata(product_code, product_name)
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        print('res_create=', res_create)
        assert res_create['status_code'] == 201

        TestStock.prod_folio_1 = res_create.get('json', {}).get('folio')
        TestStock.prod_id_1 = res_create.get('json', {}).get('id')
        print('self prod folio 1===', TestStock.prod_folio_1)
        metadata['folio'] = TestStock.prod_folio_1 
        metadata['id'] = TestStock.prod_id_1
        working_group, working_cycle = self.get_group_cyle()
        TestStock.working_group = working_group
        TestStock.working_cycle = working_cycle
        prod_answers = self.production_answers(working_group, working_cycle, qty_factor)
        metadata['answers'].update(prod_answers)
        res = stock_obj.lkf_api.patch_record(metadata, TestStock.prod_id_1)
        assert res['status_code'] == 202
        record = stock_obj.get_record_by_id(TestStock.prod_id_1)
        answers = record['answers']
        production_group = answers[stock_obj.f['production_group']]
        TestStock.total_produced_1 = answers.get(stock_obj.f['total_produced'])
        total_produced = (qty_factor*10 + qty_factor*100 + qty_factor*1000)
        assert TestStock.total_produced_1 == total_produced

    def test_production_2(self):
        qty_factor = 2
        metadata = self.production_metadata(product_code_2, product_name_2)
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        assert res_create['status_code'] == 201
        TestStock.prod_folio_2 = res_create.get('json', {}).get('folio')
        TestStock.prod_id_2 = res_create.get('json', {}).get('id')
        metadata['folio'] = TestStock.prod_folio_2 
        metadata['id'] = TestStock.prod_id_2
        working_group, working_cycle = self.get_group_cyle()
        prod_answers = self.production_answers(working_group, working_cycle, qty_factor)
        metadata['answers'].update(prod_answers)
        res = stock_obj.lkf_api.patch_record(metadata, TestStock.prod_id_2)
        assert res['status_code'] == 202
        record = stock_obj.get_record_by_id(TestStock.prod_id_2)
        answers = record['answers']
        production_group = answers[stock_obj.f['production_group']]
        TestStock.total_produced_2 = answers.get(stock_obj.f['total_produced'])
        total_produced = (qty_factor*10 + qty_factor*100 + qty_factor*1000)
        assert TestStock.total_produced_2  == total_produced

    def test_production_3(self):
        qty_factor = 3
        product_code = 'LNAFP'
        product_name = 'Nandina domestica nana Firepower'
        product_department = 'LAB'
        metadata = self.production_metadata(product_code, product_name)
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        assert res_create['status_code'] == 201
        TestStock.prod_folio_3 = res_create.get('json', {}).get('folio')
        TestStock.prod_id_3 = res_create.get('json', {}).get('id')
        metadata['folio'] = TestStock.prod_folio_3 
        metadata['id'] = TestStock.prod_id_3
        working_group = TestStock.working_group
        working_cycle = TestStock.working_cycle 
        prod_answers = self.production_answers(working_group, working_cycle, qty_factor)
        metadata['answers'].update(prod_answers)
        res = stock_obj.lkf_api.patch_record(metadata, TestStock.prod_id_3)
        assert res['status_code'] == 202
        record = stock_obj.get_record_by_id(TestStock.prod_id_3)
        answers = record['answers']
        production_group = answers[stock_obj.f['production_group']]
        TestStock.total_produced_3 = answers.get(stock_obj.f['total_produced'])
        total_produced = (qty_factor*10 + qty_factor*100 + qty_factor*1000)
        assert TestStock.total_produced_3 == total_produced

    def test_move_stock_in(self):
        warehouse = 'Lab A'
        location = '10'
        location_2 = '11'
        folio = TestStock.prod_folio_1
        total_produced = TestStock.total_produced_1
        qty1, qty2 = self.do_move_stock_in(folio, warehouse, location, location_2, total_produced)
        TestStock.stock_location_1_qty = qty1
        TestStock.stock_location_2_qty = qty2

        TestStock.stock_lot_1_loc1_qty = qty1
        TestStock.stock_lot_1_loc2_qty = qty2
        assert qty1 + qty2 == total_produced

    def test_stock_inventory(self):
        warehouse = 'Lab A'
        location = '10'
        location_2 = '11'
        # product_code = TestStock.prod_folio_2
        product_code= product_code_1
        lot_number = TestStock.lot_number
        TestStock.lot_number_1 = lot_number
        total_produced = TestStock.total_produced_1
        qty1 = self.do_test_stock(product_code, lot_number, warehouse, location, TestStock.stock_location_1_qty)
        qty2 = self.do_test_stock(product_code, lot_number, warehouse, location_2, TestStock.stock_location_2_qty)
        assert qty1 + qty2 == int(total_produced)

    def test_move_stock_in_2(self):
        warehouse = 'Lab A'
        location = '10'
        location_2 = '11'
        folio = TestStock.prod_folio_2
        total_produced = TestStock.total_produced_2
        qty1, qty2 = self.do_move_stock_in(folio, warehouse, location, location_2, total_produced)
        TestStock.stock2_location_1_qty = qty1
        TestStock.stock2_location_2_qty = qty2

    def test_stock_inventory_2(self):
        warehouse = 'Lab A'
        location = '10'
        location_2 = '11'
        # product_code = TestStock.prod_folio_2
        product_code= product_code_2
        lot_number = TestStock.lot_number
        total_produced = TestStock.total_produced_2
        qty1 = self.do_test_stock(product_code, lot_number, warehouse, location, TestStock.stock2_location_1_qty)
        qty2 = self.do_test_stock(product_code, lot_number, warehouse, location_2, TestStock.stock2_location_2_qty)
        assert qty1 + qty2 == int(total_produced)

    def test_move_stock_in_3(self):
        warehouse = 'Lab A'
        location = '10'
        location_2 = '11'
        folio = TestStock.prod_folio_3
        total_produced = TestStock.total_produced_3
        qty1, qty2 = self.do_move_stock_in(folio, warehouse, location, location_2, total_produced)
        TestStock.stock_lot_3_loc1_qty = qty1
        TestStock.stock_lot_3_loc2_qty = qty2
        assert qty1 + qty2 == total_produced

    def test_stock_inventory_3(self):
        warehouse = 'Lab A'
        location = '10'
        location_2 = '11'
        # product_code = TestStock.prod_folio_2
        product_code= product_code_1
        lot_number = TestStock.lot_number
        total_produced = TestStock.total_produced_3
        location_1_lote_qty = TestStock.stock_lot_1_loc1_qty + TestStock.stock_lot_3_loc1_qty
        location_2_lote_qty = TestStock.stock_lot_1_loc2_qty + TestStock.stock_lot_3_loc2_qty
        qty1 = self.do_test_stock(product_code, lot_number, warehouse, location, location_1_lote_qty)
        qty2 = self.do_test_stock(product_code, lot_number, warehouse, location_2, location_2_lote_qty)
        assert qty1 == location_1_lote_qty
        assert qty2 == location_2_lote_qty
        TestStock.stock3_location_1_qty = qty1 + qty2
        assert TestStock.stock_lot_3_loc1_qty + TestStock.stock_lot_3_loc2_qty == int(total_produced)

    def test_move_stock_location_1(self):
        warehouse_from = 'Lab A'
        location_from = '10'
        product_lot = TestStock.lot_number
        stock_location_1_qty = TestStock.stock_location_1_qty
        warehouse_to = 'Lab A'
        location_to = '100'
        move_qty = 1 if int(stock_location_1_qty * .1) == 0 else int(stock_location_1_qty * .1)
        metadata = self.move_metadata(product_code_1, product_lot, warehouse_from, location_from, warehouse_to, location_to, move_qty)
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        qty = self.do_test_stock(product_code_1, product_lot, warehouse_to, location_to, move_qty)
        #TODO REVISAR DESCUENT EN UBICACION ANTIGUA
        TestStock.stock_move_location_1_qty = move_qty
        assert qty == move_qty

    def test_move_stock_location_2(self):
        warehouse_from = 'Lab A'
        location_from = '11'
        product_lot = TestStock.lot_number
        stock_location_2_qty = TestStock.stock2_location_2_qty
        warehouse_to = 'Lab A'
        location_to = '100'
        move_qty = int(stock_location_2_qty * .1)
        metadata = self.move_metadata(product_code_1, product_lot, warehouse_from, location_from, warehouse_to, location_to, move_qty)
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        qty = self.do_test_stock(product_code_1, product_lot, warehouse_to, location_to, move_qty, extra_qty = TestStock.stock_move_location_1_qty)
        print('asi regresa... qty', qty)
        TestStock.stock_move_location_2_qty = qty
        # assert qty == move_qty
        assert (move_qty + TestStock.stock_move_location_1_qty )== qty

    def test_move_stock_warehouse(self):
        warehouse_from = 'Lab A'
        location_from = '10'
        product_lot = TestStock.lot_number
        stock_location_1_qty = TestStock.stock_location_1_qty
        print('stock_location_1_qty', stock_location_1_qty)
        warehouse_to = 'Lab B'
        location_to = '41'
        move_qty = 1 if int(stock_location_1_qty * .1) == 0 else int(stock_location_1_qty * .1)
        metadata = self.move_metadata(product_code_1, product_lot, warehouse_from, location_from, warehouse_to, location_to, move_qty)
        print('metadata', metadata)
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        print('res_create', res_create)
        qty = self.do_test_stock(product_code_1, product_lot, warehouse_to, location_to, move_qty)
        print('qty', qty)
        TestStock.stock_move_wh_1_qty = move_qty
        assert qty == move_qty

    def test_adjustment_qty(self):
        warehouse_from = 'Lab A'
        location_from = '11'
        product_lot = TestStock.lot_number
        stock_location_2_qty = TestStock.stock_location_2_qty
        warehouse_to = 'Lab A'
        location_to = '201'
        actual_qty = TestStock.stock_location_1_qty
        actual_qty -= TestStock.stock_move_location_1_qty 
        actual_qty -= TestStock.stock_move_wh_1_qty 
        new_qty =  actual_qty + 10
        print('new_qty', new_qty)
        metadata = self.adjust_metadata(product_code_1, product_stage_1, warehouse_from, location_from, warehouse_to, location_to, new_qty)
        print('adjust metadata metadata', metadata)
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        print('adjust res create', res_create)
        qty = self.do_test_stock(product_code_1, product_lot, warehouse_to, location_to, new_qty)
        print('adjust qtye', qty)
        assert qty == new_qty

    def test_seleccion_planta1(self):
        product_code = product_code_1
        product_name = product_name_1 
        product_stage = 'S2'
        product_lot = TestStock.lot_number_1
        stock_location_1_qty = TestStock.stock_location_1_qty
        warehouse = 'Lab A'
        location = '10'
        warehouse_to = 'Team 1 A'
        location_to = 'Team 1'
        move_qty = 1 if int(stock_location_1_qty * .1) == 0 else int(stock_location_1_qty * .1)
        metadata = self.seleccion_planta_metadata(product_code, product_name, product_lot, product_stage, warehouse, location, warehouse_to, location_to, move_qty)
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        print('res_create', res_create)
        assert res_create['status_code'] == 201

    def test_stock_inventory_out(self):
        product_code = product_code_1
        lot_number = TestStock.lot_number
        warehouse = 'Lab A'
        location = '10'
        # Deberíamos tener esto
        stock_res_loc1 = stock_obj.get_invtory_record_by_product(stock_obj.FORM_INVENTORY_ID, product_code, lot_number, warehouse, location)
        print('stock_res', stock_res_loc1)
        #stock_location_1_qty = TestStock.stock_location_3_qty
        stock_location_1_qty = TestStock.stock_location_1_qty
        move_qty = 1 if int(stock_location_1_qty * .1) == 0 else int(stock_location_1_qty * .1)
        print('move_qty', move_qty)
        print('stock_location_1_qty', stock_location_1_qty)
        stock_out = stock_location_1_qty - move_qty
        lot_number = TestStock.lot_number
        print('stock_out', stock_out)
        qty = self.do_test_stock(product_code, lot_number, warehouse, location, stock_out)
        print('qty', qty)
        assert qty == stock_out
        
##### Tests ######

    # def test_production_s3(self):
    #     qty_factor = 1
    #     product_code = 'LNAFP'
    #     product_name = 'Nandina domestica nana Firepower'
    #     product_department = 'LAB'
    #     metadata = self.production_metadata(product_code, product_name)
    #     res_create = stock_obj.lkf_api.post_forms_answers(metadata)
    #     assert res_create['status_code'] == 201
    #     TestStock.prod_folio_1 = res_create.get('json', {}).get('folio')
    #     TestStock.prod_id_1 = res_create.get('json', {}).get('id')
    #     print('self prod folio 1===', TestStock.prod_folio_1)
    #     metadata['folio'] = TestStock.prod_folio_1 
    #     metadata['id'] = TestStock.prod_id_1
    #     working_group, working_cycle = self.get_group_cyle()
    #     TestStock.working_group = working_group
    #     TestStock.working_cycle = working_cycle
    #     prod_answers = self.production_answers(working_group, working_cycle, qty_factor)
    #     metadata['answers'].update(prod_answers)
    #     res = stock_obj.lkf_api.patch_record(metadata, TestStock.prod_id_1)
    #     assert res['status_code'] == 202
    #     record = stock_obj.get_record_by_id(TestStock.prod_id_1)
    #     answers = record['answers']
    #     production_group = answers[stock_obj.f['production_group']]
    #     TestStock.total_produced_1 = answers.get(stock_obj.f['total_produced'])
    #     total_produced = (qty_factor*10 + qty_factor*100 + qty_factor*1000)
    #     assert TestStock.total_produced_1 == total_produced

    # def test_production_2_s3(self):
    #     qty_factor = 2
    #     metadata = self.production_metadata(product_code_2, product_name_2)
    #     res_create = stock_obj.lkf_api.post_forms_answers(metadata)
    #     assert res_create['status_code'] == 201
    #     TestStock.prod_folio_2 = res_create.get('json', {}).get('folio')
    #     TestStock.prod_id_2 = res_create.get('json', {}).get('id')
    #     metadata['folio'] = TestStock.prod_folio_2 
    #     metadata['id'] = TestStock.prod_id_2
    #     working_group, working_cycle = self.get_group_cyle()
    #     prod_answers = self.production_answers(working_group, working_cycle, qty_factor)
    #     metadata['answers'].update(prod_answers)
    #     res = stock_obj.lkf_api.patch_record(metadata, TestStock.prod_id_2)
    #     assert res['status_code'] == 202
    #     record = stock_obj.get_record_by_id(TestStock.prod_id_2)
    #     answers = record['answers']
    #     production_group = answers[stock_obj.f['production_group']]
    #     TestStock.total_produced_2 = answers.get(stock_obj.f['total_produced'])
    #     total_produced = (qty_factor*10 + qty_factor*100 + qty_factor*1000)
    #     assert TestStock.total_produced_2  == total_produced

    # def test_production_3_s3(self):
    #     qty_factor = 3
    #     product_code = 'LNAFP'
    #     product_name = 'Nandina domestica nana Firepower'
    #     product_department = 'LAB'
    #     metadata = self.production_metadata(product_code, product_name)
    #     res_create = stock_obj.lkf_api.post_forms_answers(metadata)
    #     assert res_create['status_code'] == 201
    #     TestStock.prod_folio_3 = res_create.get('json', {}).get('folio')
    #     TestStock.prod_id_3 = res_create.get('json', {}).get('id')
    #     metadata['folio'] = TestStock.prod_folio_3 
    #     metadata['id'] = TestStock.prod_id_3
    #     working_group = TestStock.working_group
    #     working_cycle = TestStock.working_cycle 
    #     prod_answers = self.production_answers(working_group, working_cycle, qty_factor)
    #     metadata['answers'].update(prod_answers)
    #     res = stock_obj.lkf_api.patch_record(metadata, TestStock.prod_id_3)
    #     assert res['status_code'] == 202
    #     record = stock_obj.get_record_by_id(TestStock.prod_id_3)
    #     answers = record['answers']
    #     production_group = answers[stock_obj.f['production_group']]
    #     TestStock.total_produced_3 = answers.get(stock_obj.f['total_produced'])
    #     total_produced = (qty_factor*10 + qty_factor*100 + qty_factor*1000)
    #     assert TestStock.total_produced_3 == total_produced

    # def test_move_stock_in_s3(self):
    #     warehouse = 'Lab A'
    #     location = '10'
    #     location_2 = '11'
    #     folio = TestStock.prod_folio_1
    #     total_produced = TestStock.total_produced_1
    #     qty1, qty2 = self.do_move_stock_in(folio, warehouse, location, location_2, total_produced)
    #     TestStock.stock_location_1_qty = qty1
    #     TestStock.stock_location_2_qty = qty2

    #     TestStock.stock_lot_1_loc1_qty = qty1
    #     TestStock.stock_lot_1_loc2_qty = qty2
    #     assert qty1 + qty2 == total_produced

    # def test_stock_inventory_s3(self):
    #     warehouse = 'Lab A'
    #     location = '10'
    #     location_2 = '11'
    #     # product_code = TestStock.prod_folio_2
    #     product_code= product_code_1
    #     lot_number = TestStock.lot_number
    #     TestStock.lot_number_1 = lot_number
    #     total_produced = TestStock.total_produced_1
    #     qty1 = self.do_test_stock(product_code, lot_number, warehouse, location, TestStock.stock_location_1_qty)
    #     qty2 = self.do_test_stock(product_code, lot_number, warehouse, location_2, TestStock.stock_location_2_qty)
    #     assert qty1 + qty2 == int(total_produced)

    # def test_move_stock_in_2_s3(self):
    #     warehouse = 'Lab A'
    #     location = '10'
    #     location_2 = '11'
    #     folio = TestStock.prod_folio_2
    #     total_produced = TestStock.total_produced_2
    #     qty1, qty2 = self.do_move_stock_in(folio, warehouse, location, location_2, total_produced)
    #     TestStock.stock2_location_1_qty = qty1
    #     TestStock.stock2_location_2_qty = qty2

    # def test_stock_inventory_2_s3(self):
    #     warehouse = 'Lab A'
    #     location = '10'
    #     location_2 = '11'
    #     # product_code = TestStock.prod_folio_2
    #     product_code= product_code_2
    #     lot_number = TestStock.lot_number
    #     total_produced = TestStock.total_produced_2
    #     qty1 = self.do_test_stock(product_code, lot_number, warehouse, location, TestStock.stock2_location_1_qty)
    #     qty2 = self.do_test_stock(product_code, lot_number, warehouse, location_2, TestStock.stock2_location_2_qty)
    #     assert qty1 + qty2 == int(total_produced)

    # def test_move_stock_in_3_s3(self):
    #     warehouse = 'Lab A'
    #     location = '10'
    #     location_2 = '11'
    #     folio = TestStock.prod_folio_3
    #     total_produced = TestStock.total_produced_3
    #     qty1, qty2 = self.do_move_stock_in(folio, warehouse, location, location_2, total_produced)
    #     TestStock.stock_lot_3_loc1_qty = qty1
    #     TestStock.stock_lot_3_loc2_qty = qty2
    #     assert qty1 + qty2 == total_produced

    # def test_stock_inventory_3_s3(self):
    #     warehouse = 'Lab A'
    #     location = '10'
    #     location_2 = '11'
    #     # product_code = TestStock.prod_folio_2
    #     product_code= product_code_1
    #     lot_number = TestStock.lot_number
    #     total_produced = TestStock.total_produced_3
    #     location_1_lote_qty = TestStock.stock_lot_1_loc1_qty + TestStock.stock_lot_3_loc1_qty
    #     location_2_lote_qty = TestStock.stock_lot_1_loc2_qty + TestStock.stock_lot_3_loc2_qty
    #     qty1 = self.do_test_stock(product_code, lot_number, warehouse, location, location_1_lote_qty)
    #     qty2 = self.do_test_stock(product_code, lot_number, warehouse, location_2, location_2_lote_qty)
    #     assert qty1 == location_1_lote_qty
    #     assert qty2 == location_2_lote_qty
    #     TestStock.stock3_location_1_qty = qty1 + qty2
    #     assert TestStock.stock_lot_3_loc1_qty + TestStock.stock_lot_3_loc2_qty == int(total_produced)

    # def test_move_stock_location_1_s3(self):
    #     warehouse_from = 'Lab A'
    #     location_from = '10'
    #     product_lot = TestStock.lot_number
    #     stock_location_1_qty = TestStock.stock_location_1_qty
    #     warehouse_to = 'Lab A'
    #     location_to = '100'
    #     move_qty = 1 if int(stock_location_1_qty * .1) == 0 else int(stock_location_1_qty * .1)
    #     metadata = self.move_metadata(product_code_1, product_lot, warehouse_from, location_from, warehouse_to, location_to, move_qty)
    #     res_create = stock_obj.lkf_api.post_forms_answers(metadata)
    #     qty = self.do_test_stock(product_code_1, product_lot, warehouse_to, location_to, move_qty)
    #     #TODO REVISAR DESCUENT EN UBICACION ANTIGUA
    #     TestStock.stock_move_location_1_qty = move_qty
    #     assert qty == move_qty

    # def test_move_stock_location_2_s3(self):
    #     warehouse_from = 'Lab A'
    #     location_from = '11'
    #     product_lot = TestStock.lot_number
    #     stock_location_2_qty = TestStock.stock2_location_2_qty
    #     warehouse_to = 'Lab A'
    #     location_to = '100'
    #     move_qty = int(stock_location_2_qty * .1)
    #     metadata = self.move_metadata(product_code_1, product_lot, warehouse_from, location_from, warehouse_to, location_to, move_qty)
    #     res_create = stock_obj.lkf_api.post_forms_answers(metadata)
    #     qty = self.do_test_stock(product_code_1, product_lot, warehouse_to, location_to, move_qty, extra_qty = TestStock.stock_move_location_1_qty)
    #     print('asi regresa... qty', qty)
    #     TestStock.stock_move_location_2_qty = qty
    #     # assert qty == move_qty
    #     assert (move_qty + TestStock.stock_move_location_1_qty )== qty

    # def test_move_stock_warehouse_s3(self):
    #     warehouse_from = 'Lab A'
    #     location_from = '10'
    #     product_lot = TestStock.lot_number
    #     stock_location_1_qty = TestStock.stock_location_1_qty
    #     print('stock_location_1_qty', stock_location_1_qty)
    #     warehouse_to = 'Lab B'
    #     location_to = '41'
    #     move_qty = 1 if int(stock_location_1_qty * .1) == 0 else int(stock_location_1_qty * .1)
    #     metadata = self.move_metadata(product_code_1, product_lot, warehouse_from, location_from, warehouse_to, location_to, move_qty)
    #     print('metadata', metadata)
    #     res_create = stock_obj.lkf_api.post_forms_answers(metadata)
    #     print('res_create', res_create)
    #     qty = self.do_test_stock(product_code_1, product_lot, warehouse_to, location_to, move_qty)
    #     print('qty', qty)
    #     TestStock.stock_move_wh_1_qty = move_qty
    #     assert qty == move_qty

    # def test_adjustment_qty_s3(self):
    #     warehouse_from = 'Lab A'
    #     location_from = '11'
    #     product_lot = TestStock.lot_number
    #     stock_location_2_qty = TestStock.stock_location_2_qty
    #     warehouse_to = 'Lab A'
    #     location_to = '201'
    #     actual_qty = TestStock.stock_location_1_qty
    #     actual_qty -= TestStock.stock_move_location_1_qty 
    #     actual_qty -= TestStock.stock_move_wh_1_qty 
    #     new_qty =  actual_qty + 10
    #     print('new_qty', new_qty)
    #     metadata = self.adjust_metadata(product_code_1, product_stage_3, warehouse_from, location_from, warehouse_to, location_to, new_qty)
    #     print('adjust metadata metadata', metadata)
    #     res_create = stock_obj.lkf_api.post_forms_answers(metadata)
    #     print('adjust res create', res_create)
    #     qty = self.do_test_stock(product_code_1, product_lot, warehouse_to, location_to, new_qty)
    #     print('adjust qtye', qty)
    #     assert qty == new_qty

    def test_seleccion_planta1_s3(self):
        product_code = product_code_1
        product_name = product_name_1 
        product_stage = 'S3'
        product_lot = TestStock.lot_number_1
        stock_location_1_qty = TestStock.stock_location_1_qty
        warehouse = 'Lab A'
        location = '10'
        warehouse_to = 'Team 1 A'
        location_to = 'Team 1'
        move_qty = 1 if int(stock_location_1_qty * .1) == 0 else int(stock_location_1_qty * .1)
        metadata = self.seleccion_planta_metadata(product_code, product_name, product_lot, product_stage, warehouse, location, warehouse_to, location_to, move_qty)
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        print('res_create', res_create)
        assert res_create['status_code'] == 201
    
    def test_inventory_pull_out(self):
        product_code = product_code_1
        product_name = product_name_1 
        product_stage = 'S2'
        product_lot = TestStock.lot_number_1
        stock_location_1_qty = TestStock.stock_location_1_qty
        warehouse = 'Lab A'
        location = '10'
        warehouse_to = 'Team 1 A'
        location_to = 'Team 1'
        move_qty = 1 if int(stock_location_1_qty * .1) == 0 else int(stock_location_1_qty * .1)
        metadata = self.pull_out_metadata(product_code, product_name, product_lot, product_stage, warehouse, location, warehouse_to, location_to, move_qty)
        res_create = stock_obj.lkf_api.post_forms_answers(metadata)
        print('res_create', res_create)
        assert res_create['status_code'] == 201
    
    def test_production_greenhouse(self):
        qty_factor = 1
        product_code = 'LNAFP'
        product_name = 'Nandina domestica nana Firepower'
        product_department = 'LAB'
        total_produced = (qty_factor*10 + qty_factor*100 + qty_factor*1000)
        metadata = self.production_metadata_greenhouse(product_code, product_name, total_produced)
        res_create = stock_obj_greenhouse.lkf_api.post_forms_answers(metadata)
        assert res_create['status_code'] == 201
        TestStock.prod_folio_1 = res_create.get('json', {}).get('folio')
        TestStock.prod_id_1 = res_create.get('json', {}).get('id')
        metadata['folio'] = TestStock.prod_folio_1 
        metadata['id'] = TestStock.prod_id_1
        working_group, working_cycle = self.get_group_cyle()
        TestStock.working_group = working_group
        TestStock.working_cycle = working_cycle
        prod_answers = self.production_answers(working_group, working_cycle, qty_factor)
        metadata['answers'].update(prod_answers)
        res = stock_obj_greenhouse.lkf_api.patch_record(metadata, TestStock.prod_id_1)
        assert res['status_code'] == 202
        record = stock_obj_greenhouse.get_record_by_id(TestStock.prod_id_1)
        answers = record['answers']
        production_group = answers[stock_obj.f['production_group']]
        TestStock.total_produced_1 = answers.get(stock_obj.f['total_produced'])
        assert TestStock.total_produced_1 == total_produced

    def test_move_stock_in_greenhouse(self):
        warehouse = 'Lab A'
        location = '10'
        location_2 = '11'
        folio = TestStock.prod_folio_1
        total_produced = TestStock.total_produced_1
        qty1, qty2 = self.do_move_stock_in_greenhouse(folio, warehouse, location, location_2, total_produced)
        TestStock.stock_location_1_qty = qty1
        TestStock.stock_location_2_qty = qty2

        TestStock.stock_lot_1_loc1_qty = qty1
        TestStock.stock_lot_1_loc2_qty = qty2       
        assert qty1 + qty2 == total_produced
        
        
    def get_test_stock_qty_greenhouse(self, product_code, lot_number, warehouse, location, qty, extra_qty=0):
        current_record = {}
        current_record.get('answers')
        record = stock_obj_greenhouse.get_record_by_id(TestStock.prod_id_1)
        answers = record['answers']
        plant_info = record['answers'].get(stock_obj.f['product_recipe'], {})
        plant_code = plant_info.get(stock_obj.f['product_code'])
        lot_number = record['answers'].get(stock_obj.f['production_lote'], {})

        new_production = {}
        recipes = None

        recipes = stock_obj.get_plant_recipe([plant_code,], stage=[4, 'Ln72',])
        week = record['answers'].get(stock_obj.f['production_week'])
        year = record['answers'].get(stock_obj.f['production_year'])
        if not week or not year:
            return []
        production_date = time.strptime('{} {} 1'.format(year, week), '%Y %W %w')
        production_date = datetime.fromtimestamp(time.mktime(production_date))
        recipe = stock_obj.select_S4_recipe(recipes[plant_code], week)
        grow_weeks = recipe.get('S4_growth_weeks')
        ready_date = production_date + timedelta(weeks=grow_weeks)
        calc_lot_number = int(ready_date.strftime('%Y%W'))
        lot_number = record['answers'].get(stock_obj.f['production_lote'], calc_lot_number)
        
        total_produced =0
        force_lot = False
        for production in record['answers'].get(stock_obj.f['production_group'], []):
            production_status = production.get(stock_obj.f['production_status'],'progress')
            if production_status == 'progress':
                force_lot = True

            total_hours = stock_obj.calc_work_hours(production)
            production[stock_obj.f['set_total_hours']] = round(total_hours, 2)

            total_produced += production[stock_obj.f['set_total_produced']]
            if production_status == 'progress':
                containers_out = production[stock_obj.f['set_total_produced']]
            else:
                containers_out = 0



          
            qty_per_container = recipe.get(stock_obj.f['prod_qty_per_container'], [])
            if qty_per_container:
                if type(qty_per_container) == list and qty_per_container[0]:
                    qty_per_container = int( qty_per_container[0] )
                else:
                    qty_per_container = int(qty_per_container)
            else:
                qty_per_container = 0 

            container_type = None
            if qty_per_container:
                container_type = 'ln{}'.format(qty_per_container)
            

            total_eu = 1 * containers_out 
            flats_per_hour = total_eu / float(total_hours)



            production[stock_obj.f['set_products_per_hours']] = round(flats_per_hour, 2) # Plants per Hour
            production[stock_obj.f['production_status']] = 'posted'
            plant_date = production[stock_obj.f['set_production_date']]
            plant_date = datetime.strptime(plant_date, '%Y-%m-%d')


            production[stock_obj.f['product_lot']] = lot_number
            plan_defults = {
                'qty':0,
                'plant_date':plant_date, 
                'qty_per_container':qty_per_container,
                'container_type':container_type,
                'recipe':recipe}
            new_production[lot_number] = new_production.get(lot_number, plan_defults)
            new_production[lot_number]['qty'] += containers_out

        res = []
        total_produced = record['answers'].get(stock_obj.f['total_produced'])
        planting_house = warehouse
        for lot_number, plant_data in new_production.items():
            res.append(self.calculates_inventory_greenhouse(plant_info, planting_house, lot_number, plant_data, grow_weeks, qty=total_produced, force_lot=force_lot))
            return res
            
        #plant_data is an object with the following keys 'qty','recipe', 'planted_date'
    def calculates_inventory_greenhouse(self, plant_info, warehouse, ready_date, plant_data, grow_weeks, force_lot=False, qty=0):
        plant_code = plant_info[stock_obj.f['product_code']]
        greenhouse_inventory = stock_obj.get_record_greenhouse_inventory(ready_date, warehouse, plant_code)
        plant_yearWeek = plant_data.get('plant_date').strftime('%Y%W')
        qty_produced = plant_data.get('qty',0)
        container_type = plant_data.get('container_type')
        S4_overage = plant_data.get('recipe').get('S4_overage', 0)
        qty_proyected = math.floor(qty_produced * (1 - S4_overage))
        if not greenhouse_inventory:

            answers_to_record = {
                stock_obj.f['product_lot_produced']: qty_produced,
                stock_obj.f['product_estimated_ready_date']: ready_date, # Estimated Ready Week
                stock_obj.f['product_lot']: ready_date,
                stock_obj.f['product_lot_actuals']: qty_produced, # Containers on hand
                stock_obj.f['product_lot_proyected_qty']: qty_proyected , # Proyected Containers on hand
                stock_obj.f['product_lot_created_week']: int(plant_yearWeek),
                stock_obj.f['product_recipe']: plant_info,
                stock_obj.f['product_growth_week']: grow_weeks,
                stock_obj.CATALOG_WAREHOUSE_OBJ_ID: {stock_obj.f['warehouse']:warehouse},
                stock_obj.f['inventory_status']: 'active',
                stock_obj.f['product_grading_pending']: 'grading_pending'
            }
            if container_type:
                answers_to_record.update({stock_obj.f['product_container_type']:container_type})
            metadata = stock_obj.lkf_api.get_metadata(stock_obj_greenhouse.FORM_INVENTORY_ID)
            if force_lot:
                #metadata['kwargs'] = {'production':qty_produced}
                stock_obj.cache_set({
                    '_id': f'{plant_code}_{ready_date}_{warehouse}',
                    'production':qty_produced,
                    'product_lot':ready_date,
                    'product_code':plant_code,
                    'warehouse': warehouse,
                    })
            metadata.update({
                'properties': {
                    "device_properties":{
                        "system": "Script",
                        "process": 'GreenHouse Inventory',
                        "action": 'Upsert Inventory GreenHouse',
                    }
                },
                'answers': answers_to_record
            })

            resp_create = stock_obj.lkf_api.post_forms_answers(metadata, jwt_settings_key='APIKEY_JWT_KEY')
            return resp_create
        new_qty_produced = qty_produced + greenhouse_inventory['answers'].get(stock_obj.f['product_lot_produced'], 0)
        new_qty_proyected = qty_proyected + greenhouse_inventory['answers'].get(stock_obj.f['product_lot_proyected_qty'], 0)
        new_qty_flats = qty_produced + greenhouse_inventory['answers'].get(stock_obj.f['product_lot_actuals'], 0)
        
        greenhouse_inventory['answers'][stock_obj.f['product_lot_produced']] = new_qty_produced
        greenhouse_inventory['answers'][stock_obj.f['product_lot_proyected_qty']] = new_qty_proyected
        greenhouse_inventory['answers'][stock_obj.f['product_lot_actuals']] = new_qty_flats
        if force_lot:
            stock_obj.cache_set({
                '_id': f'{plant_code}_{ready_date}_{warehouse}',
                'production':qty_produced,
                'product_lot':ready_date,
                'product_code':plant_code,
                'warehouse': warehouse,
                'record_id': stock_obj.record_id
                })
            greenhouse_inventory['properties'] = {'kwargs':{'production':qty_produced}}
            greenhouse_inventory['kwargs'] = {'production':qty_produced}
        resp_update = stock_obj.lkf_api.patch_record(greenhouse_inventory, jwt_settings_key='APIKEY_JWT_KEY')
        return resp_update
        
    def do_test_stock_greenhouse(self, product_code, lot_number, warehouse, location, qty, extra_qty=0):
        res = self.get_test_stock_qty_greenhouse(product_code, lot_number, warehouse, location, qty, extra_qty)
        data = json.loads(res[0]['data'])
        folio = data['id']
        greenhouse_inventory_record = stock_obj_greenhouse.get_record_by_id(folio)
        answers = greenhouse_inventory_record['answers']
        acutalas_1 = greenhouse_inventory_record['answers'][stock_obj.f['actuals']]
        catalog_records = self.get_test_stock_qty_catalog(product_code, lot_number, warehouse, location)
        for rec in catalog_records:
            catalog_records_qty = rec.get(stock_obj.f['actuals'])
            assert qty == catalog_records_qty
        return acutalas_1
        
    def test_stock_inventory_greenhouse(self):
        warehouse = 'Lab A'
        location = '10'
        product_code= product_code_1
        lot_number = TestStock.prod_folio_1
        total_produced = TestStock.total_produced_1
        qty = self.do_test_stock_greenhouse(product_code, lot_number, warehouse, location, TestStock.stock_location_1_qty)
        assert qty == int(total_produced)
    
    def test_production_greenhouse_2(self):
        qty_factor = 2
        product_code = 'LNAFP'
        product_name = 'Nandina domestica nana Firepower'
        product_department = 'LAB'
        total_produced = (qty_factor*10 + qty_factor*100 + qty_factor*1000)
        metadata = self.production_metadata_greenhouse(product_code, product_name, total_produced)
        res_create = stock_obj_greenhouse.lkf_api.post_forms_answers(metadata)
        assert res_create['status_code'] == 201
        TestStock.prod_folio_2 = res_create.get('json', {}).get('folio')
        TestStock.prod_id_2 = res_create.get('json', {}).get('id')
        print('self prod folio 2===', TestStock.prod_folio_2)
        metadata['folio'] = TestStock.prod_folio_2 
        metadata['id'] = TestStock.prod_id_2
        working_group, working_cycle = self.get_group_cyle()
        TestStock.working_group = working_group
        TestStock.working_cycle = working_cycle
        prod_answers = self.production_answers(working_group, working_cycle, qty_factor)
        metadata['answers'].update(prod_answers)
        res = stock_obj_greenhouse.lkf_api.patch_record(metadata, TestStock.prod_id_2)
        assert res['status_code'] == 202
        record = stock_obj_greenhouse.get_record_by_id(TestStock.prod_id_2)
        answers = record['answers']
        production_group = answers[stock_obj.f['production_group']]
        TestStock.total_produced_2 = answers.get(stock_obj.f['total_produced'])
        assert TestStock.total_produced_2 == total_produced
    
    def test_move_stock_in_2_greenhouse(self):
        warehouse = 'Lab A'
        location = '10'
        location_2 = '11'
        folio = TestStock.prod_folio_2
        total_produced = TestStock.total_produced_2
        qty1, qty2 = self.do_move_stock_in_greenhouse(folio, warehouse, location, location_2, total_produced)
        TestStock.stock2_location_1_qty = qty1
        TestStock.stock2_location_2_qty = qty2    

    def test_production_greenhouse_3(self):
        qty_factor = 3
        product_code = 'LNAFP'
        product_name = 'Nandina domestica nana Firepower'
        product_department = 'LAB'
        total_produced = (qty_factor*10 + qty_factor*100 + qty_factor*1000)
        metadata = self.production_metadata_greenhouse(product_code, product_name, total_produced)
        res_create = stock_obj_greenhouse.lkf_api.post_forms_answers(metadata)
        assert res_create['status_code'] == 201
        TestStock.prod_folio_3 = res_create.get('json', {}).get('folio')
        TestStock.prod_id_3 = res_create.get('json', {}).get('id')
        print('self prod folio 3===', TestStock.prod_folio_3)
        metadata['folio'] = TestStock.prod_folio_3 
        metadata['id'] = TestStock.prod_id_3
        working_group, working_cycle = self.get_group_cyle()
        TestStock.working_group = working_group
        TestStock.working_cycle = working_cycle
        prod_answers = self.production_answers(working_group, working_cycle, qty_factor)
        metadata['answers'].update(prod_answers)
        res = stock_obj_greenhouse.lkf_api.patch_record(metadata, TestStock.prod_id_3)
        assert res['status_code'] == 202
        record = stock_obj_greenhouse.get_record_by_id(TestStock.prod_id_3)
        answers = record['answers']
        production_group = answers[stock_obj.f['production_group']]
        TestStock.total_produced_3 = answers.get(stock_obj.f['total_produced'])
        assert TestStock.total_produced_3 == total_produced
        

    def test_move_stock_in_3_greenhouse(self):
        warehouse = 'Lab A'
        location = '10'
        location_2 = '11'
        folio = TestStock.prod_folio_3
        total_produced = TestStock.total_produced_3
        qty1, qty2 = self.do_move_stock_in_greenhouse(folio, warehouse, location, location_2, total_produced)
        TestStock.stock_lot_3_loc1_qty = qty1
        TestStock.stock_lot_3_loc2_qty = qty2
        assert qty1 + qty2 == total_produced
