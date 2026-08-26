# coding: utf-8

"""
Helpers del flujo completo de guardia: checkin/checkout de turno y
creación de áreas. Todo pega contra la API/BD real (sin mocks).
"""

import time
from datetime import datetime

from bson import ObjectId
from couchdb.http import ResourceNotFound

from lkf_modules.accesos.items.scripts.Accesos.accesos_testing import get_shift_data, do_checkin, do_checkout


def asegurar_turno_abierto(acceso_obj, location, area, fotografia):
    """
    Revisa el estatus del turno de la caseta; si ya está abierto lo cierra
    primero (forzando el cierre), y siempre abre un turno nuevo y limpio.
    Devuelve el checkin_id del turno recién abierto.
    """
    turn_data = get_shift_data(acceso_obj, {"location": location, "area": area})
    status_turn = (turn_data.get('guard') or {}).get('status_turn')

    if status_turn == 'Turno Abierto':
        checkin_id = (turn_data.get('booth_status') or {}).get('checkin_id')
        assert checkin_id, f"Turno reportado como abierto pero sin checkin_id: {turn_data}"
        do_checkout(acceso_obj, {
            "location": location,
            "area": area,
            "checkin_id": checkin_id,
            "guards": [],
            "forzar": True,
            "comments": "Cierre automático antes de iniciar la prueba",
        })

    start_turn_data = do_checkin(acceso_obj, {
        "location": location,
        "area": area,
        "employee_list": [],
        "fotografia": fotografia,
        "nombre_suplente": "",
        "checkin_id": "",
    })
    assert start_turn_data.get('status_code') in (200, 201, 202), (
        f"No se pudo abrir el turno: {start_turn_data}"
    )
    checkin_id = start_turn_data['json']['id']
    assert checkin_id, "El turno se abrio pero no regreso checkin_id"
    return checkin_id


def crear_area(area_obj, nombre_area, ubicacion, foto_area, latitude, longitude, tipo_de_area='Bodega'):
    """
    Crea un área nueva en el catálogo `areas_de_las_ubicaciones` (usada
    después para configurar un rondín). Replica el flujo real de
    update_area.py::create_new_area sin pasar por sys_argv/script runner.
    """
    area_obj.geolocation_area = {'latitude': latitude, 'longitude': longitude}
    data = {
        'ubicacion': ubicacion,
        'nombre_nueva_area': nombre_area,
        'foto_area': foto_area,
        'qr_area': '',
        'tipo_de_area': tipo_de_area,
    }
    response = area_obj.create_new_area(data)
    assert response is not None, (
        f"El area '{nombre_area}' ya existia en '{ubicacion}' (create_new_area no creo nada nuevo)"
    )
    assert response.get('status_code') == 201, f"No se pudo crear el area '{nombre_area}': {response}"
    return response


def asignar_tag_id_area(area_obj, nombre_area, ubicacion):
    """
    Asigna al área ya creada un tag_id con forma de URL
    (https://web.clave10.com/areas/{ObjectId aleatorio}) vía update_area
    (PATCH), en un paso separado de la creación para probar también la
    funcionalidad de actualizar áreas. Devuelve la URL asignada.
    """
    tag_url = f"https://web.clave10.com/areas/{ObjectId()}"
    data = {
        'ubicacion': ubicacion,
        'area': nombre_area,
        'qr_area': tag_url,
    }
    response = area_obj.update_area(data)
    assert response is not None, f"No se encontro el area '{nombre_area}' para actualizar el tag_id"
    assert response.get('status_code') in (200, 201, 202), (
        f"No se pudo actualizar el tag_id del area '{nombre_area}': {response}"
    )
    return tag_url


def sincronizar_area_couchdb(obj, area_id):
    """
    Empuja el área (ya creada/actualizada en Mongo) al catálogo de CouchDB
    `areas_de_las_ubicaciones`. `create_new_area`/`post_forms_answers` y
    `update_area`/`patch_forms_answers` NO hacen esto por su cuenta -- la
    sincronización a catálogo es un paso explícito y separado.
    """
    return obj.lkf_api.sync_catalogs_records({
        "catalogs_ids": [obj.AREAS_DE_LAS_UBICACIONES_CAT_ID],
        "form_answers_ids": [area_id],
        "status": "created",
    })


def verificar_area_en_couchdb(obj, area_id, intentos=5, espera_segundos=1):
    """
    Confirma que el área ya sea consultable directo en CouchDB
    (misma base que respalda /v2/catalog-records/{catalog_id}/record/{id}/),
    con reintentos cortos por si la sincronización tarda en quedar visible.
    """
    db_name = f"catalog_records_{obj.AREAS_DE_LAS_UBICACIONES_CAT_ID}"
    db = obj.get_couch_user_db(db_name)
    ultimo_error = None
    for _ in range(intentos):
        try:
            return db[area_id]
        except ResourceNotFound as e:
            ultimo_error = e
            time.sleep(espera_segundos)
    raise AssertionError(
        f"El area {area_id} no aparecio en CouchDB ({db_name}) tras {intentos} intentos: {ultimo_error}"
    )


def verificar_areas_en_catalogo_rondines(rondines_obj, nombres_area, ubicacion):
    """
    Verifica que las áreas ya sean visibles para configurar un rondín,
    usando el mismo método real que consume la UI de recorridos
    (get_catalog_areas, script rondines.py) -- no CouchDB directo ni el
    registro de catálogo por separado. Este método consulta Mongo
    directamente y EXIGE que el área tenga `area_tag_id` asignado
    ($exists) para aparecer, por eso se llama después de
    `asignar_tag_id_area`, nunca antes.
    """
    areas_disponibles = rondines_obj.get_catalog_areas(ubicacion=ubicacion)
    faltantes = [n for n in nombres_area if n not in areas_disponibles]
    assert not faltantes, (
        f"Estas areas no aparecen en get_catalog_areas para '{ubicacion}': {faltantes}. "
        f"Disponibles: {areas_disponibles}"
    )
    return areas_disponibles


def crear_rondin(rondines_obj, nombre_rondin, ubicacion, areas, fecha_hora_programada, duracion_estimada='17 minutos'):
    """
    Crea la plantilla de rondín (form configuracion_de_recorridos), tipo
    "Responsable en Turno": create_rondin -> rondin_asignado_a resuelve al
    usuario que hace la llamada (no a un usuario explícito). `areas` debe
    ser una lista de nombres EXACTOS (mismo string que en el catálogo
    areas_de_las_ubicaciones) -- si no matchean, el rondín se crea igual
    pero esa área queda sin geolocalización/foto/tag_id.

    El workflow config_recorridos.py (runtime: after) suscribe el cron en
    Airflow de forma síncrona con este mismo POST, así que la respuesta ya
    trae el `dag_id` -- no hace falta pollear get_recorridos para esto
    (esperar_dag_id queda solo como fallback si viniera vacío).
    Devuelve (record_id, dag_id).
    """
    rondin_data = {
        "nombre_rondin": nombre_rondin,
        "duracion_estimada": duracion_estimada,
        "ubicacion": ubicacion,
        "areas": areas,
        "grupo_asignado": "",
        "fecha_hora_programada": fecha_hora_programada,
        "programar_anticipacion": "no",
        "cuanto_tiempo_de_anticipacion": 0,
        "cuanto_tiempo_de_anticipacion_expresado_en": "",
        "tiempo_para_ejecutar_tarea": 30,
        "tiempo_para_ejecutar_tarea_expresado_en": "minutos",
        "la_tarea_es_de": "cuenta_con_una_recurrencia",
        "la_recurrencia_cuenta_con_fecha_final": "no",
        "fecha_final_recurrencia": "",
        "accion_recurrencia": "programar",
        "se_repite_cada": "semana",
        "cron_conf": "",
        "tipo_rondin": "QR",
        "tipo_asignacion": "responsable_en_turno",
        "asignado_a": "responsable_en_turno",
        "que_dias_de_la_semana": ["lunes"],
        "sucede_recurrencia": ["dia_de_la_semana"],
        "area": "",
    }
    # bug conocido en create_rondin: si rondin_data incluye la key 'cron_id'
    # lanza NameError (usa una variable 'valor' que no existe) -- por eso
    # no se manda esa key aquí.
    response = rondines_obj.create_rondin(rondin_data=rondin_data)
    assert response.get('status_code') in (200, 201, 202), f"No se pudo crear el rondin: {response}"
    record_id = response.get('json', {}).get('id')
    assert record_id, f"El rondin se creo pero no regreso id: {response}"
    dag_id = response.get('json', {}).get('dag_id', '')
    return record_id, dag_id


def esperar_dag_id(rondines_obj, record_id, intentos=10, espera_segundos=3):
    """
    Fallback por si create_rondin regresara dag_id vacío (no debería, ver
    docstring de crear_rondin). Hace polling sobre get_recorridos.
    """
    for _ in range(intentos):
        recorridos = rondines_obj.get_recorridos(date_from=None, date_to=None, limit=100, offset=0)
        for r in recorridos:
            if str(r.get('_id')) == str(record_id) and r.get('dag_id'):
                return r['dag_id']
        time.sleep(espera_segundos)
    raise AssertionError(
        f"El rondin {record_id} no obtuvo dag_id tras {intentos} intentos (~{intentos * espera_segundos}s)"
    )


def ejecutar_rondin(rondines_obj, dag_id):
    """
    Dispara el DAG en Airflow (run_cron/run_rondin) -- Airflow solo encola
    la corrida (queued), no espera a que termine. La tarea real
    (bitacora_rondines) se crea después, de forma asíncrona.

    OJO: esto pega directo a `airflow_bob` (192.168.0.25:5000 en este
    ambiente), un servicio interno de la red de producción -- NO
    alcanzable desde el contenedor de test (da
    `ConnectionError: Connection refused`). No se usa en
    test_flujo_guardia.py por esto; el test solo verifica que `dag_id`
    quede asignado (create_rondin ya lo regresa), sin ejecutar el DAG de
    verdad. Deja este helper para cuando se corra desde dentro de esa red.
    """
    response = rondines_obj.run_cron(dag_id)
    assert response.get('status_code') in (200, 201, 202), (
        f"No se pudo correr el rondin (dag_id={dag_id}): {response}"
    )
    return response


def esperar_bitacora_rondin(rondines_obj, ubicacion, nombre_rondin, intentos=8, espera_segundos=5):
    """
    Espera a que Airflow (task LKFLogin -> CreateRecord) cree la instancia
    real del rondín en bitacora_rondines tras ejecutar_rondin. Devuelve el
    primer registro que matchea ubicacion+nombre_recorrido.

    Solo tiene sentido llamarlo si `ejecutar_rondin` sí corrió (ver nota
    ahí sobre por qué no se usa en test_flujo_guardia.py en este entorno).

    Nota: en config_recorridos.py el bloque que asignaría un usuario
    (assigne_user_id/assign) está comentado en el código actual -- no
    asumas que `asignado_a` viene poblado solo con esto, puede requerir un
    claim_rondin/assign_rondin explícito aparte.
    """
    for _ in range(intentos):
        resultado = rondines_obj.get_bitacora(ubicacion=ubicacion, nombre_rondin=nombre_rondin, limit=5)
        registros = resultado.get('data', [])
        if registros:
            return registros[0]
        time.sleep(espera_segundos)
    raise AssertionError(
        f"No aparecio ningun registro en bitacora_rondines para '{nombre_rondin}' en '{ubicacion}' "
        f"tras {intentos} intentos (~{intentos * espera_segundos}s)"
    )


def crear_bitacora_rondin_directo(rondines_obj, nombre_rondin, ubicacion, tipo_rondin='qr'):
    """
    Crea directo el registro de bitacora_rondines (la instancia real del
    rondín, distinta de la plantilla configuracion_de_recorridos) -- esto
    es lo que normalmente crea el operador Airflow "CreateRecord" al
    correr el DAG (ver config_recorridos.py, task 'create_and_assign').
    Se usa porque este entorno de test no puede alcanzar airflow_bob (ver
    ejecutar_rondin). Devuelve el _id del nuevo registro, que la app móvil
    usa literalmente como `rondin_id` en sus docs de CouchDB.
    """
    answers = {
        rondines_obj.CONFIGURACION_RECORRIDOS_OBJ_ID: {
            rondines_obj.Location.f['location']: ubicacion,
            rondines_obj.mf['nombre_del_recorrido']: nombre_rondin,
        },
        rondines_obj.f['fecha_programacion']: rondines_obj.today_str(date_format='datetime'),
        rondines_obj.mf['estatus_del_recorrido']: 'programado',
        rondines_obj.rondin_keys['tipo_rondin']: tipo_rondin,
    }
    metadata = rondines_obj.lkf_api.get_metadata(form_id=rondines_obj.BITACORA_RONDINES)
    metadata.update({'answers': answers})
    response = rondines_obj.lkf_api.post_forms_answers(metadata)
    assert response.get('status_code') in (200, 201, 202), f"No se pudo crear bitacora_rondines: {response}"
    rondin_id = response.get('json', {}).get('id')
    assert rondin_id, f"bitacora_rondines se creo pero no regreso id: {response}"
    return rondin_id


def simular_check_area_couchdb(
    rondines_obj, rondin_id, area_nombre, ubicacion, tag_id, foto_area,
    tipo_de_area='Bodega', user_id=10, user_name='Emiliano Zapata', comentario='Todo en orden',
):
    """
    Simula el doc CouchDB type:"check_area" que la app móvil crea al
    responder un punto del rondín (ver clave10-app/utils/rondines.ts::
    createCheckAreaDocument). `status_user='completed'` + `status='synced'`
    son exactamente lo que exige `sync_records()` del backend para
    procesarlo y crear el registro real en check_ubicaciones. Devuelve
    (doc_id, doc_rev).
    """
    ahora = int(time.time())
    doc = {
        "_id": str(ObjectId()),
        "rondin_id": rondin_id,
        "type": "check_area",
        "status_user": "completed",
        "created_at": ahora,
        "updated_at": ahora,
        "timezone": "America/Monterrey",
        "created_by_id": user_id,
        "created_by_name": user_name,
        "geolocation": {"lat": 0, "long": 0},
        "record": {
            "tag_id": tag_id,
            "ubicacion": ubicacion,
            "area": area_nombre,
            "tipo_de_area": tipo_de_area,
            "foto_del_area": foto_area,
            "inspeccion": [],
            "checked": True,
            "checked_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "evidencia_incidencia": [],
            "documento_incidencia": [],
            "incidencias": [],
            "comentario_check_area": comentario,
            "inspeccion_respuestas": [],
        },
        "status": "synced",
    }
    db = rondines_obj.get_couch_user_db(f"clave_{user_id}")
    doc_id, doc_rev = db.save(doc)
    return doc_id, doc_rev


def simular_rondin_couchdb(rondines_obj, rondin_id, nombre_rondin, ubicacion, areas_check, user_id=10, user_name='Emiliano Zapata'):
    """
    Simula el doc CouchDB type:"rondin" (instancia de trabajo offline de
    la app móvil, ver clave10-app/utils/mapConfigToRondinDoc.ts). Su `_id`
    DEBE ser el mismo `_id` del registro real en bitacora_rondines
    (`rondin_id`) -- el backend hace un lookup directo por ese _id, no por
    folio/nombre. `status_user='completed'` es lo único que
    `complete_rondines`/`sync_records` revisan para marcar
    estatus_del_recorrido='realizado'; no valida que cada área en
    `areas_check` esté `checked=True`.
    """
    ahora = int(time.time())
    doc = {
        "_id": rondin_id,
        "type": "rondin",
        "inbox": False,
        "status": "synced",
        "status_user": "completed",
        "created_at": ahora,
        "updated_at": ahora,
        "created_by_id": user_id,
        "created_by_name": user_name,
        "geolocation": {"lat": 0, "long": 0},
        "record": {
            "user_name": user_name,
            "nombre_rondin": nombre_rondin,
            "ubicacion_rondin": ubicacion,
            "duracion_estimada": "17 minutos",
            "fecha_programada": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "tipo_rondin": "qr",
            "fecha_inicio": "", "fecha_finalizacion": "", "fecha_pausa": "", "fecha_reanudacion": "",
            "ultimo_check_area_id": "",
            "comentarios_rondin": [],
            "incidencia_rondin": [],
            "check_areas": areas_check,
        },
    }
    db = rondines_obj.get_couch_user_db(f"clave_{user_id}")
    doc_id, doc_rev = db.save(doc)
    return doc_id, doc_rev


def sincronizar_rondin_offline(rondines_obj, user_id=10, user_name='Emiliano Zapata', user_email='seguridad@linkaform.com'):
    """
    Simula la llamada que hace la app móvil (syncRondinToLkf) para que el
    backend procese los docs CouchDB pendientes. `sync_records` NO filtra
    por id -- escanea TODA la base `clave_{user_id}` buscando docs con
    status_user='completed' + status='synced' (de cualquier tipo), crea el
    registro real en check_ubicaciones por cada check_area, y actualiza
    estatus_del_recorrido en bitacora_rondines según el status_user del
    doc rondin. OJO: es un scan de cuenta completa, no solo de esta
    corrida -- puede ser lento si hay muchos docs históricos pendientes.
    """
    rondines_obj.user_id = user_id
    rondines_obj.user_name = user_name
    rondines_obj.user_email = user_email
    rondines_obj.geolocation = []
    rondines_obj.cr_db = rondines_obj.get_couch_user_db(f"clave_{user_id}")
    return rondines_obj.sync_records([])


def verificar_estatus_rondin(rondines_obj, ubicacion, nombre_rondin, estatus_esperado='realizado', intentos=5, espera_segundos=2):
    """
    Confirma que bitacora_rondines quedó con el estatus esperado tras
    sincronizar_rondin_offline, con reintentos cortos por si el patch aún
    no se refleja en la siguiente lectura.
    """
    ultimo = None
    for _ in range(intentos):
        resultado = rondines_obj.get_bitacora(ubicacion=ubicacion, nombre_rondin=nombre_rondin, limit=5)
        registros = resultado.get('data', [])
        if registros:
            ultimo = registros[0]
            if ultimo.get('estatus_recorrido') == estatus_esperado:
                return ultimo
        time.sleep(espera_segundos)
    raise AssertionError(
        f"El rondin '{nombre_rondin}' en '{ubicacion}' no quedo con estatus '{estatus_esperado}' "
        f"tras {intentos} intentos: {ultimo}"
    )
