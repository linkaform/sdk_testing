# coding: utf-8

import uuid
import pytest
from datetime import datetime
from pytz import timezone

from .fixtures import *
from .helpers import (
    asegurar_turno_abierto,
    crear_area,
    asignar_tag_id_area,
    sincronizar_area_couchdb,
    verificar_area_en_couchdb,
    verificar_areas_en_catalogo_rondines,
    crear_rondin,
    esperar_dag_id,
    crear_bitacora_rondin_directo,
    simular_check_area_couchdb,
    simular_rondin_couchdb,
    sincronizar_rondin_offline,
    verificar_estatus_rondin,
)
from .data.flujo_guardia_data import LOCATION, AREA, FOTOGRAFIA_TURNO, GEOLOCATION_BASE, AREAS_NUEVAS


@pytest.mark.e2e
def test_flujo_guardia_turno_areas_y_rondin(acceso_obj, area_obj, rondines_obj):
    """
    Flujo completo del guardia:
      1. Asegura que el turno de la caseta quede abierto (si ya estaba
         abierto lo cierra primero, para arrancar siempre limpio).
      2. Crea 4 áreas nuevas con nombre único (fecha + run_id) para poder
         identificarlas como datos de prueba, con foto y geolocalización
         propias (la primera en el punto base, las otras 3 movidas ~5-10m).
      3. Ya creada cada área, le asigna un tag_id (URL con ObjectId
         aleatorio) en un paso de actualización aparte (update_area/PATCH),
         probando así también esa funcionalidad.
      4. Sincroniza cada área al catálogo de CouchDB (sync_catalogs_records
         -- create_new_area/update_area NO lo hacen solos) y verifica que
         ya sea consultable ahí directo.
      5. Verifica que las 4 áreas ya sean visibles usando el mismo método
         real que consume la configuración de rondines
         (get_catalog_areas, script rondines.py) -- ese método exige
         area_tag_id asignado, por eso se verifica hasta el final.
      6. Crea un rondín tipo "Responsable en Turno" usando las 4 áreas y
         verifica que quede con `dag_id` asignado (create_rondin ya lo
         regresa directo -- el workflow config_recorridos.py suscribe el
         cron en Airflow de forma síncrona con el POST).
      7. Como no se puede disparar el DAG real (ver nota abajo), crea
         directo el registro de bitacora_rondines (lo que haría el
         operador de Airflow) y simula los docs de CouchDB que la app
         móvil generaría al "responder" el rondín: un `check_area` por
         cada área (status_user=completed) + un `rondin`
         (status_user=completed) referenciándolas.
      8. Dispara el mismo procesamiento que usa el backend cuando la app
         llama syncRondinToLkf (`sync_records`), y verifica que
         bitacora_rondines quede con estatus_del_recorrido='realizado'.

    Este test NO ejecuta el DAG (run_rondin/run_cron): eso pega directo al
    servicio interno airflow_bob (192.168.1.25:5000 en este ambiente), que
    no es alcanzable desde el contenedor de test. Alcanzar `dag_id`
    asignado ya es suficiente para confirmar que el rondín quedó bien
    configurado y suscrito. Ver `ejecutar_rondin`/`esperar_bitacora_rondin`
    en helpers.py si esto se corre desde dentro de esa red.
    """
    marca_tiempo = datetime.now(timezone('America/Monterrey')).strftime('%m-%d-%H:%M:%S')
    run_id = uuid.uuid4().hex[:8]

    checkin_id = asegurar_turno_abierto(acceso_obj, LOCATION, AREA, FOTOGRAFIA_TURNO)
    assert checkin_id

    base_lat, base_lng = GEOLOCATION_BASE
    areas_creadas = []
    for idx, area_def in enumerate(AREAS_NUEVAS, start=1):
        nombre_area = f"area de prueba {idx} - {marca_tiempo} - {run_id}"
        lat = base_lat + area_def["lat_offset"]
        lng = base_lng + area_def["lng_offset"]

        response = crear_area(
            area_obj,
            nombre_area=nombre_area,
            ubicacion=LOCATION,
            foto_area=[{"file_name": f"area_{idx}.png", "file_url": area_def["foto_url"]}],
            latitude=lat,
            longitude=lng,
        )
        tag_url = asignar_tag_id_area(area_obj, nombre_area, LOCATION)

        area_id = response.get('json', {}).get('id')
        sincronizar_area_couchdb(area_obj, area_id)
        doc_couch = verificar_area_en_couchdb(area_obj, area_id)

        areas_creadas.append({
            "nombre": nombre_area,
            "id": area_id,
            "tag_id": tag_url,
            "couch_rev": doc_couch.get('_rev'),
            "foto_url": area_def["foto_url"],
        })

    assert len(areas_creadas) == 4
    assert all(a["id"] for a in areas_creadas), f"Alguna area no regreso id: {areas_creadas}"

    nombres_creados = [a["nombre"] for a in areas_creadas]
    verificar_areas_en_catalogo_rondines(rondines_obj, nombres_creados, LOCATION)

    nombre_rondin = f"Rondin de prueba - {marca_tiempo} - {run_id}"
    fecha_hora_programada = datetime.now(timezone('America/Monterrey')).strftime('%Y-%m-%d %H:%M:%S')

    record_id, dag_id = crear_rondin(rondines_obj, nombre_rondin, LOCATION, nombres_creados, fecha_hora_programada)
    if not dag_id:
        dag_id = esperar_dag_id(rondines_obj, record_id)

    assert dag_id, f"El rondin {record_id} no obtuvo dag_id"

    rondin_id = crear_bitacora_rondin_directo(rondines_obj, nombre_rondin, LOCATION)

    check_docs = []
    areas_check = []
    for a in areas_creadas:
        foto = [{"file_name": f"{a['nombre']}.png", "file_url": a["foto_url"]}]
        doc_id, doc_rev = simular_check_area_couchdb(
            rondines_obj, rondin_id,
            area_nombre=a["nombre"], ubicacion=LOCATION, tag_id=a["tag_id"], foto_area=foto,
        )
        check_docs.append({"id": doc_id, "rev": doc_rev})
        areas_check.append({
            "tag_id": a["tag_id"], "ubicacion": LOCATION, "area": a["nombre"],
            "tipo_de_area": "Bodega", "foto_del_area": foto,
            "checked": True, "checked_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "check_area_id": doc_id,
        })

    simular_rondin_couchdb(rondines_obj, rondin_id, nombre_rondin, LOCATION, areas_check)

    sincronizar_rondin_offline(rondines_obj)
    bitacora_final = verificar_estatus_rondin(rondines_obj, LOCATION, nombre_rondin, estatus_esperado='realizado')

    print(f"\nTurno abierto con checkin_id={checkin_id}")
    print("Areas creadas para esta corrida:")
    for a in areas_creadas:
        print(f"  - {a['nombre']} (id={a['id']}, tag_id={a['tag_id']}, couch_rev={a['couch_rev']})")
    print(f"\nRondin creado: {nombre_rondin} (record_id={record_id}, dag_id={dag_id})")
    print(f"Bitacora del rondin (instancia real): rondin_id={rondin_id}")
    print(f"Checks simulados en CouchDB: {check_docs}")
    print(f"Estatus final del rondin: {bitacora_final.get('estatus_recorrido')!r}")
