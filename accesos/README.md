# Módulo Accesos — Guía de Pruebas

Este README explica cómo están organizadas las pruebas del módulo Accesos y cómo agregar nuevas correctamente.

## Estructura

Cada sección del módulo sigue esta estructura:

    accesos/
    ├── conftest.py
    ├── pytest.ini
    └── <seccion>/
        ├── data/
        ├── unit/
        ├── integration/
        └── e2e/

Las secciones corresponden a las funcionalidades del módulo: `menus`, `turnos`, `rondines`, `passes`, etc.

---

## Las tres capas de prueba

### Unit — `unit/`

Pruebas aisladas. No tocan la red ni la base de datos. Todo lo externo se simula con `mocker`.

**Cuándo usar:** siempre que quieras probar la lógica interna de una función sin depender de servicios externos.

**Señal de que un test pertenece aquí:** usa `mocker.patch.object`.

Lo que se mockea es la capa de base de datos (`cr.aggregate`), no la función completa. Así el código real corre y solo se simula la respuesta de MongoDB:

    mocker.patch.object(
        accesos_no_api.cr,
        "aggregate",
        return_value=[]
    )

    resultado = accesos_no_api.get_config_accesos()

### Integration — `integration/`

Pruebas contra la API real de Linkaform y la BD real. Sin mocks.

**Cuándo usar:** para verificar que una función se comunica correctamente con los servicios externos.

**Requisito:** credenciales válidas en `account_settings.py` y conexión activa.

**Señal de que un test pertenece aquí:** llama a métodos reales sin ningún mock.

### E2E — `e2e/`

Flujos completos de usuario. Varios pasos encadenados donde el resultado de uno alimenta al siguiente.

**Cuándo usar:** cuando quieras probar una operación completa de punta a punta, por ejemplo: obtener menú → cargar turno → hacer checkin → hacer checkout.

**Regla:** un archivo por flujo. Si el primer paso falla, el flujo se detiene.

---

## Cómo nombrar los archivos

| Patrón                      | Capa        | Ejemplo                          |
| --------------------------- | ----------- | -------------------------------- |
| `test_<funcion>.py`         | Unit        | `test_get_config_accesos.py`     |
| `test_<funcion>_api.py`     | Integration | `test_get_config_accesos_api.py` |
| `test_flujo_<escenario>.py` | E2E         | `test_flujo_menu_turnos.py`      |

---

## Cómo nombrar los tests

Dentro de cada archivo, el nombre del test describe el comportamiento que se verifica:

    test_get_config_accesos_retorna_dict
    test_get_config_accesos_sin_datos_retorna_dict_vacio
    test_get_config_accesos_menus_es_lista_no_vacia

El patrón es: `test_<funcion>_<condicion>` o `test_<funcion>_<resultado_esperado>`.

---

## Cuántos tests por archivo

**Unit e Integration:** varios tests por archivo, agrupados por la función que prueban.

    unit/
    └── test_get_config_accesos.py
        ├── test_instancia_accesos_no_api
        ├── test_get_config_accesos_retorna_dict
        ├── test_get_config_accesos_sin_datos_retorna_dict_vacio
        └── test_get_config_accesos_menus_es_lista_no_vacia

**E2E:** un flujo por archivo.

---

## Markers

Todos los tests deben tener el marker de su capa. Están registrados en `pytest.ini`:

    @pytest.mark.unit
    @pytest.mark.integration
    @pytest.mark.e2e

Sin el marker, pytest lanza un warning y no puedes filtrar por capa al correr las pruebas.

### Múltiples markers en un mismo test

Un test puede tener más de un marker apilando los decoradores. Además del marker de capa (`unit`/`integration`/`e2e`), se puede agregar un marker de funcionalidad para filtrar un subconjunto específico dentro de esa capa:

    @pytest.mark.integration
    @pytest.mark.do_access
    def test_do_access_pase_activo_permite_acceso(acceso_obj, mock_pase_do_access):
        ...

Para correr solo los tests que cumplan **todas** las condiciones (AND):

    pytest -m "integration and do_access"

También se puede filtrar con `or` (cualquiera de los dos) o `not` (excluir):

    pytest -m "integration or e2e"
    pytest -m "integration and not do_access"

### Registrar un marker nuevo

Antes de usar un marker de funcionalidad (como `do_access`) hay que declararlo en `pytest.ini`, en la sección `markers`, con una descripción corta de qué agrupa:

    markers =
        unit: Pruebas unitarias (sin red, sin BD, todo mockeado)
        integration: Pruebas de integración (requieren API de Linkaform activa)
        e2e: Pruebas end-to-end (requieren API de Linkaform activa y entorno de pruebas configurado)
        do_access: Pruebas de acceso (requieren API de Linkaform activa y entorno de pruebas configurado)

Si se usa un marker sin registrarlo, pytest lanza `PytestUnknownMarkWarning` (o falla si el proyecto corre con `--strict-markers`).

**Cuidado con nombres de test duplicados:** si dos funciones en el mismo archivo tienen el mismo nombre, Python sobreescribe la primera al importar el módulo — pytest solo colecciona la segunda, y los markers de la primera (incluyendo markers de funcionalidad como `do_access`) desaparecen silenciosamente sin ningún warning. Si vas a copiar un test para adaptarlo a otra capa (por ejemplo de `integration` a `e2e`), cambia el nombre de la función.

---

## Docstrings

Cada test debe tener un docstring con al menos uno de los siguientes puntos:

1.  Qué comportamiento valida
2.  Por qué importa — qué se rompe en producción si falla

    @pytest.mark.unit
    def test_get_config_accesos_sin_datos_retorna_dict_vacio(accesos_no_api, mocker):
    """
    Cuando MongoDB no encuentra configuración para el usuario,
    get_config_accesos() debe retornar un dict vacío, no None.

        Por qué importa: la UI debe poder manejar este caso sin que
        el script falle en producción.
        """

---

## Fixtures disponibles

Definidas en `conftest.py`, disponibles en todos los tests sin necesidad de importarlas.

| Fixture             | Autenticación | Usuario                    |
| ------------------- | ------------- | -------------------------- |
| `accesos_no_api`    | JWT           | seguridad@linkaform.com    |
| `accesos_api`       | API Key       | seguridad@linkaform.com    |
| `accesos_api_15864` | API Key       | juan.escutia@linkaform.com |

---

## Carpeta `data/`

Cada sección puede tener una carpeta `data/` para constantes compartidas entre capas: claves esperadas, valores válidos, datos de entrada reutilizables.

**Cuándo crear un archivo en `data/`:** cuando el mismo dato lo usan dos o más tests de distintas capas.

**Cuándo dejarlo en el archivo del test:** cuando el dato es específico de un solo flujo.
