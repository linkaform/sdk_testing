# coding: utf-8

"""
Imprime un índice de todos los tests de sdk_testing, uno por línea:

    ruta::test | tipo | TB-XXX | bug(folio) | primera línea del docstring

Arriba de cada archivo va el docstring del módulo (script y funciones que
prueba). Solo lee el código con ast: no importa nada ni corre pytest.

Uso (desde la raíz de sdk_testing):
    python3 .claude/skills/buscar-tests/scripts/indice_tests.py [filtro]

El filtro opcional deja solo los archivos cuya ruta lo contenga
(p. ej. "paqueteria" o "entradas_salidas").
"""

import ast
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
TIPOS = ("unit", "integration", "e2e")
TB = re.compile(r"TB-\d{3}")


def nombre_marker(deco):
    """Devuelve (nombre, args) de un @pytest.mark.<nombre>(...)."""
    nodo = deco.func if isinstance(deco, ast.Call) else deco
    if isinstance(nodo, ast.Attribute):
        args = [a.value for a in getattr(deco, "args", []) if isinstance(a, ast.Constant)]
        return nodo.attr, args
    return None, []


def primera_linea(texto):
    for linea in (texto or "").strip().splitlines():
        if linea.strip():
            return linea.strip()
    return ""


def tests_de(arbol):
    """Funciones test_* a nivel módulo y dentro de clases Test*."""
    for nodo in arbol.body:
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) and nodo.name.startswith("test"):
            yield nodo.name, nodo
        elif isinstance(nodo, ast.ClassDef) and nodo.name.startswith("Test"):
            for hijo in nodo.body:
                if isinstance(hijo, (ast.FunctionDef, ast.AsyncFunctionDef)) and hijo.name.startswith("test"):
                    yield f"{nodo.name}::{hijo.name}", hijo


def main():
    filtro = sys.argv[1] if len(sys.argv) > 1 else ""
    archivos = sorted(
        p for p in RAIZ.rglob("test_*.py")
        if "_test_template" not in p.parts and ".git" not in p.parts and filtro in str(p)
    )
    total = 0
    for archivo in archivos:
        ruta = archivo.relative_to(RAIZ)
        try:
            arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        except SyntaxError as e:
            print(f"\n## {ruta}  (no se pudo leer: {e})")
            continue
        print(f"\n## {ruta}")
        doc_modulo = " ".join((ast.get_docstring(arbol) or "").split())
        if doc_modulo:
            print(f"   {doc_modulo}")
        for nombre, func in tests_de(arbol):
            markers = [nombre_marker(d) for d in func.decorator_list]
            tipo = ",".join(m for m, _ in markers if m in TIPOS) or "-"
            bugs = ",".join(f"bug({a})" for m, args in markers if m == "bug" for a in args) or "-"
            doc = ast.get_docstring(func) or ""
            tbs = ",".join(dict.fromkeys(TB.findall(doc))) or "-"
            print(f"{ruta}::{nombre} | {tipo} | {tbs} | {bugs} | {primera_linea(doc)}")
            total += 1
    print(f"\n{total} tests en {len(archivos)} archivos")


if __name__ == "__main__":
    main()
