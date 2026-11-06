---
name: buscar-tests
description: Dado un problema descrito en palabras ("al editar un pase se duplican los acompañantes", "la salida marca mal la duración", "rompí get_paquetes"), busca en sdk_testing qué tests existentes lo cubren, dice cuáles correr y con qué comando, consulta su estado en Notion (Testing Backend) y, si no hay cobertura, lo dice y crea un ticket en Tareas del Equipo asignado a QA (Citlali) con el contexto, sin explicar a nadie cómo hacer el test. Úsala siempre que alguien de Clave 10 pregunte qué test correr, qué pruebas cubren una sección/función/script de Accesos, si hay tests para un bug o ticket 2610-XXXX, o quiera validar un cambio en accesos_utils.py o en un script de Accesos, aunque no diga "test" explícitamente.
---

# Buscar tests en sdk_testing

Alguien (dev, QA, soporte) te cuenta qué le está pasando o qué cambió, y tú
le dices **qué tests de sdk_testing ya existen para eso, cómo correrlos y
qué tan confiables son hoy**. Si no hay test que lo cubra, lo dices sin
rodeos: ese hueco es información valiosa para QA.

No escribes tests, no explicas cómo escribirlos y no corres pytest. La
persona corre los tests en su contenedor; tú solo le das la lista y los
comandos, porque los tests de integración y E2E escriben datos reales en
preprod y quien los corre debe decidir cuándo hacerlo. Los tests nuevos los
diseña QA: si falta uno, creas un ticket asignado a Citlali.

## Paso 1. Entender el problema

De la descripción saca, aunque sea tentativamente:

- **Sección del menú** (Accesos, Pases de Entrada, Paquetería, Rondines,
  Turnos, Control de patio…) y, si se puede, la **opción** ("+ Nuevo Pase",
  "Dentro", "Entregados"…).
- **Script y funciones del backend** involucrados (`do_out`,
  `update_full_pass`, `get_paquetes`…). Si la persona solo describe el
  síntoma, búscalos tú con `grep` del texto, campo u `option` que menciona,
  en los dos lugares donde vive el backend de Accesos (solo lectura):
  - `~/clave10-sdk/addons/modules/accesos/items/scripts/Accesos/`: los
    scripts de entrada (`incidencias.py`, `paqueteria.py`…) y
    `accesos_utils.py`. El script recibe un `option` y despacha a un método.
  - `~/clave10-sdk/addons/lkf_addons/addons/accesos/app.py`: donde está la
    lógica de muchos de esos métodos (`update_full_pass`,
    `create_incidence`…). Si el método no está en `accesos_utils.py`, está
    aquí.
- **Folio de ticket** si lo menciona (2610-XXXX). Si no lo menciona y tú
  lo encuentras buscando texto (en Notion o en mensajes de commit),
  preséntalo como probable ("parece ser el 2610-1369"), no como un hecho:
  un título parecido no garantiza que sea el mismo bug.

Cuando cites archivos del backend, da la ruta desde `addons/`
(`lkf_addons/addons/accesos/app.py`, `modules/.../Accesos/incidencias.py`).
Un `accesos/app.py` a secas se confunde con una ruta de tests.

Si la descripción es demasiado vaga para ubicar siquiera la sección, pregunta
una sola cosa concreta (p. ej. "¿esto pasa en Pases de Entrada o en
Bitácora?") antes de buscar.

## Paso 2. Buscar en el código

Corre el índice desde la raíz de sdk_testing:

```bash
python3 .claude/skills/buscar-tests/scripts/indice_tests.py            # todo
python3 .claude/skills/buscar-tests/scripts/indice_tests.py paqueteria # solo rutas que contengan "paqueteria"
```

Cada línea es `ruta::test | tipo | TB-XXX | bug(folio) | primera línea del
docstring`, y arriba de cada archivo va el docstring del módulo, que nombra
el script y las funciones que prueba. Con eso ubicas candidatos por sección
(carpeta), por función y por TB.

Después confirma con `grep -rn` en `accesos/` las funciones que encontraste
en el Paso 1: un test puede llamar a la función desde un fixture o helper
(`fixtures.py`, `helpers.py`, `data/`) sin nombrarla en su docstring. Lee el
docstring completo de cada candidato para saber **qué valida de verdad**.

Si hay folio de ticket, búscalo en los markers: `@pytest.mark.bug(<folio>)`.

**Cita solo tests que existan.** Cada test que recomiendes debe salir del
índice o de un `grep`, con su ruta exacta. Si algo se parece pero no prueba
lo que la persona describe, dilo como "relacionado" y explica la diferencia
en vez de presentarlo como cobertura.

## Paso 3. Consultar Notion (si está disponible)

Si tienes las herramientas de Notion, consulta la BD **Clave10 - Testing
Backend** (data source `collection://c29a38c2-ccd2-46ef-bf9d-a5d40e460825`)
con los TB que encontraste:

```sql
SELECT "ID del test", "Nombre del test", "Estado", "Resultado", url
FROM "collection://c29a38c2-ccd2-46ef-bf9d-a5d40e460825"
WHERE "ID del test" IN ('TB-152', 'TB-154')
```

Lo que te importa:

- **Resultado**: `Pasa`, `Bug abierto`, `Bug corregido`, o vacío (aún no se
  ha corrido). Un test con *Bug abierto* **va a fallar** hoy y es esperado:
  avísalo para que no lo confundan con algo que rompieron.
- **Estado**: `Icebox` significa que esa funcionalidad está en pausa; dilo.
- La `url` de la página, para que puedan ver el detalle.

Si Notion no está conectado o la consulta falla, sigue sin él y dilo en una
línea al final ("no pude consultar Notion; el estado de cada TB no está
verificado"). En Testing Backend solo lees: no cambies nada ahí. Lo único
que escribes en Notion es el ticket para QA cuando falta cobertura.

## Paso 4. Responder

Responde en español con esta estructura. Ordena de lo más rápido a lo más
amplio (unit → integration → e2e), porque así la persona obtiene señal
pronto y solo escala si hace falta.

```markdown
**Entendí:** <una línea: sección, opción y funciones que ubicaste>

### Tests que lo cubren
1. `accesos/<seccion>/<tipo>/test_x.py::test_y` — TB-XXX · <tipo>
   Qué valida: <una línea, en palabras de negocio>
   Estado en Notion: <Pasa | Bug abierto (ticket 2610-XXXX) | sin correr | no consultado>

### Cómo correrlos
<comandos>

### Relacionados (no cubren exactamente tu caso)
<solo si hay; con la diferencia explicada>

### Huecos de cobertura
<solo si hay; ver abajo>
```

### Comandos

Los tests se corren dentro del contenedor de pruebas. Dale los comandos
listos para copiar, del más chico al más grande. El contenedor abre en
`/srv/lkf_test` (que es `addons/test`), así que el primer paso adentro es
entrar a `sdk_testing`:

```bash
cd ~/clave10-sdk/addons && ./lkf start test
```

```bash
cd sdk_testing
```

```bash
pytest accesos/<seccion>/<tipo>/test_x.py::test_y -v
```

```bash
pytest accesos/<seccion>/ -v
```

Todo comando de pytest lleva una ruta dentro de `accesos/`, también los
que filtran (`pytest accesos/ -m unit -v`, `pytest accesos/ --bug <folio> -v`).
La configuración (`pytest.ini` con el `pythonpath` de los scripts, y el
`conftest.py` que define `--bug`) vive en `accesos/`, y pytest solo la lee
si el comando apunta ahí. Un `pytest -m unit` o `pytest --bug 1477` a secas
desde `sdk_testing` falla.

Para varios tests sueltos usa `-k "test_a or test_b"`. Si hay folio de
ticket, ofrece también `pytest accesos/ --bug <folio> -v`, que corre solo
los tests ligados a ese ticket.

Cuando recomiendes tests `integration` o `e2e`, añade una línea: corren
contra preprod y crean datos reales (sin teardown). El `conftest.py`
bloquea la corrida si el entorno activo no es preprod; en ese caso se
cambia desde el host con `./lkf workon preprod` (en `~/clave10-sdk/addons`).
No sugieras `--allow-prod-integration`.

### Huecos de cobertura

Si ningún test cubre lo que describen, o solo cubre una parte, dilo primero
y con claridad: "No hay ningún test en sdk_testing que cubra <caso>." No
lo suavices recomendando tests lejanos para llenar la respuesta. Si hay
tests parecidos, puedes decir en una línea por qué no lo detectan (p. ej.
"todos mandan `acompanantes: 0`"): es un hecho sobre lo que ya existe.

Después **crea un ticket para QA** (siguiente sección) y a la persona solo
dile:

> No hay test que cubra esto. Ya le asigné el caso a Citlali (QA):
> ticket 2610-<folio>.

**No le digas cómo hacer el test**: ni qué función probar, ni de qué
tipo, ni qué debería validar, ni código, ni ofrezcas escribirlo, y no le
muestres el contenido del ticket. Si lo pide ("¿cómo lo pruebo?",
"escríbeme el test"), responde que los tests de sdk_testing los diseña y
escribe QA y que el caso ya está asignado a Citlali. QA decide qué se
prueba, la prioridad, el ID TB y dónde va; un test armado fuera de ese plan
no queda registrado en Notion y rompe el mapa de cobertura.

### Ticket para QA

Va en **Tareas del Equipo** (data source
`collection://26425e25-55ec-8017-b0cc-000bef0c8aae`). Es para Citlali: le
explica el problema y su contexto para que ella decida el test. No le dice
qué test hacer.

1. **Antes de crear, busca si ya existe.** Busca en esa base por la
   función o la sección. Si ya hay un ticket abierto asignado a Citlali para
   el mismo caso, no crees otro: dile a la persona que ya está asignado y
   el folio.
2. **Créalo** con estas propiedades:
   - `Tarea`: provisional, se corrige en el paso 3.
   - `Task Type`: `Task` · `Platform`: `["Testing"]` · `Cliente`: `["Clave10"]`
   - `Sección`: `Accesos` · `Estado`: `ToDo`
   - `Asignado a`: `["user://3bbd872b-594c-81ce-ad2c-00022fe42a91"]` (Citlali Carrillo)
   - `Test Case`: vacío. Es para tests que fallan por un bug, y aquí no hay
     test.
3. **Título con folio.** Lee `Folio Consecutivo` de la página creada y pon
   `Tarea` = `2610-<folio> · Accesos · <Opción>: <qué no se está validando>`,
   p. ej. `2610-1540 · Accesos · Pases de Entrada: no se valida editar un
   pase con acompañantes`. Usa el mismo prefijo que los tickets recientes
   de la base (hoy `2610`).
4. **Cuerpo**, con estas secciones:

   ```markdown
   ## Qué pasa
   <el problema tal como lo describió la persona, quién lo reportó y cuándo>

   ## Qué no se está validando
   <qué parte no tiene test. Si hay tests parecidos: cuáles son (ruta::test,
   TB) y por qué no lo detectan. Si no hay ninguno en la sección, dilo.>

   ## Dónde
   <funciones y archivos involucrados, con la ruta desde addons/ y la copia
   en lkf-sanic-apps si existe; sin números de línea>

   ## Contexto
   <lo que encontraste: ticket probable relacionado, commit del fix, si el
   cambio fue solo de front, etc. Omite la sección si no hay nada.>
   ```

   No incluyas cómo hacer el test, tipo, qué validar ni "Cómo reproducir".

Si no tienes las herramientas de Notion, no puedes crear el ticket: dile a
la persona que no hay test y que se lo asigne a Citlali en Tareas del
Equipo, sin más detalle.

## Ejemplo

Un caso en que hay tests parecidos pero ninguno cubre lo que preguntan.

Pregunta: "al editar un pase titular se duplican los acompañantes, ¿qué
test corro?"

Respuesta (resumida):

> **Entendí:** Pases de Entrada, editar pase;
> `lkf_addons/addons/accesos/app.py: update_full_pass`.
>
> ### Huecos de cobertura
> **No hay ningún test en sdk_testing que edite un pase con acompañantes.**
> Todos los que llaman a `update_full_pass` mandan `acompanantes: 0` y
> `acompanantes_grupo: []`, así que pasarían aunque el bug siguiera.
>
> No hay test que cubra esto. Ya le asigné el caso a Citlali (QA):
> ticket 2610-<folio>.
>
> ### Relacionados (no cubren exactamente tu caso)
> 1. `accesos/pases_entrada/integration/test_editar_pase.py::test_editar_pase_completo_guarda_los_cambios` — TB-121 · integration
>    Qué valida: editar nombre, empresa y fechas; el pase no lleva acompañantes.
>    Estado en Notion: <lo que diga la consulta>
>
> ### Cómo correrlos
> (comandos, con el aviso de preprod)
