# sdk_testing

Repositorio de pruebas automatizadas para los módulos del SDK de Linkaform.

## Requisitos

- Acceso al repositorio `addons`
- Docker
- Credenciales válidas en `account_settings.py` para los módulos que se quieran probar

## Cómo correr las pruebas

Desde la raíz de `addons`, levanta el contenedor de pruebas:

    ./lkf start test

El contenedor abre en `/srv/lkf_test` (la carpeta `addons/test`). Entra a
`sdk_testing` y corre `pytest` siempre con una ruta dentro del módulo:

    cd sdk_testing

    # Todos los tests de Accesos
    pytest accesos/ -v

    # Solo unitarios (no requieren conexión)
    pytest accesos/ -m unit -v

    # Solo integración (requieren API activa)
    pytest accesos/ -m integration -v

    # Solo E2E
    pytest accesos/ -m e2e -v

    # Una sección
    pytest accesos/entradas_salidas/ -v

    # Un archivo específico
    pytest accesos/menus/unit/test_get_config_accesos.py -v

La ruta es obligatoria: la configuración de cada módulo (`pytest.ini`, con el
`pythonpath` de sus scripts, y su `conftest.py`) vive dentro del módulo, y
pytest solo la lee si el comando apunta ahí. Un `pytest -m unit` sin ruta
desde `sdk_testing` falla al recolectar los tests.

## Estructura de un módulo

Cada módulo sigue esta estructura:

    <modulo>/
    ├── conftest.py          # Fixtures compartidas del módulo
    ├── pytest.ini           # Configuración de pytest
    └── <seccion>/
        ├── data/            # Datos de referencia compartidos entre capas
        ├── unit/            # Sin red, sin BD, todo mockeado
        ├── integration/     # Contra API real, sin mocks
        └── e2e/             # Flujos completos de usuario

Para entender cómo agregar pruebas a un módulo, consulta `accesos/README.md`.

## Convenciones

- Todos los tests deben tener `@pytest.mark.unit`, `@pytest.mark.integration` o `@pytest.mark.e2e`
- Todos los tests deben tener docstring explicando qué valida y/o por qué importa
