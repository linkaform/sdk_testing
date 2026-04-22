# sdk_testing

Repositorio de pruebas automatizadas para los módulos del SDK de Linkaform.

## Requisitos

- Acceso al repositorio `addons`
- Docker
- Credenciales válidas en `account_settings.py` para los módulos que se quieran probar

## Cómo correr las pruebas

Desde la raíz de `addons`, levanta el contenedor de pruebas:

    ./lkf start test

Una vez dentro del contenedor, usa `pytest` normalmente:

    # Todos los tests
    pytest -v

    # Solo unitarios (no requieren conexión)
    pytest -m unit -v

    # Solo integración (requieren API activa)
    pytest -m integration -v

    # Solo E2E
    pytest -m e2e -v

    # Un módulo específico
    pytest accesos/ -v

    # Un archivo específico
    pytest accesos/menus/unit/test_get_config_accesos.py -v

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

Para entender cómo agregar pruebas a un módulo, consulta el README interno de cada sección, por ejemplo `accesos/menus/README.md`.

## Convenciones

- Todos los tests deben tener `@pytest.mark.unit`, `@pytest.mark.integration` o `@pytest.mark.e2e`
- Todos los tests deben tener docstring explicando qué valida y por qué importa
