#!/usr/bin/env python3
"""
tesela-erp CLI — comandos holded-ping, load-supabase, panel-sync.

Uso:
    tesela-erp holded-ping
    tesela-erp load-supabase
    tesela-erp load-supabase --sociedad TESELA_GESTION
    tesela-erp panel-sync
"""

import sys
import argparse
from dotenv import load_dotenv
load_dotenv()  # Carga .env antes de que los módulos lean os.getenv en import time

from .extractor import EMPRESAS, ping_sociedad, sync_sociedad
from .supabase_loader import load_sociedad
from .views import refresh_views


def cmd_ping(args):
    print("─" * 50)
    print("tesela-erp holded-ping")
    print("─" * 50)
    all_ok = True
    for sociedad, key in EMPRESAS.items():
        if not key:
            print(f"  ✗ {sociedad:<20} sin API key configurada")
            all_ok = False
            continue
        result = ping_sociedad(sociedad, key)
        if result["ok"]:
            print(f"  ✓ {sociedad:<20} conectado")
        else:
            print(f"  ✗ {sociedad:<20} ERROR: {result['error']}")
            all_ok = False
    print("─" * 50)
    sys.exit(0 if all_ok else 1)


def cmd_load_supabase(args):
    print("─" * 50)
    print("tesela-erp load-supabase")
    print("─" * 50)
    all_ok = True
    target = args.sociedad.upper() if args.sociedad else None
    if target and target not in EMPRESAS:
        print(f"  ✗ Sociedad desconocida: '{target}'. Opciones: {', '.join(EMPRESAS)}")
        sys.exit(1)
    for sociedad, key in EMPRESAS.items():
        if target and sociedad != target:
            continue
        if not key:
            print(f"  ✗ {sociedad}: sin API key, saltando")
            all_ok = False
            continue
        data = sync_sociedad(sociedad, key)
        errors = data.pop("_errors", {})
        counts = load_sociedad(sociedad, data)
        summary = (
            f"{counts['contacts']} contactos, "
            f"{counts['invoices']} ventas, "
            f"{counts['bills']} compras, "
            f"{counts['projects']} proyectos"
        )
        if errors:
            failed = ", ".join(errors.keys())
            print(f"  ⚠ {sociedad}: {summary}  [{len(errors)} endpoints fallaron: {failed}]")
            all_ok = False
        else:
            print(f"  ✓ {sociedad}: {summary}")
    print("─" * 50)
    sys.exit(0 if all_ok else 1)


def cmd_panel_sync(args):
    print("─" * 50)
    print("tesela-erp panel-sync")
    print("─" * 50)
    all_ok = True
    results = refresh_views()
    for view, info in results.items():
        if info.get("ok"):
            detail = info.get("detail", "")
            print(f"  ✓ {view}: {detail}")
        else:
            print(f"  ✗ {view}: {info.get('error')}")
            all_ok = False
    print("─" * 50)
    sys.exit(0 if all_ok else 1)


def main():
    parser = argparse.ArgumentParser(prog="tesela-erp")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("holded-ping", help="Verifica conectividad con todas las cuentas Holded")

    p_load = sub.add_parser("load-supabase", help="Extrae Holded y carga en Supabase")
    p_load.add_argument("--sociedad", help="Sincronizar solo esta sociedad", default=None)

    sub.add_parser("panel-sync", help="Recalcula vistas analíticas en Supabase")

    args = parser.parse_args()

    if args.command == "holded-ping":
        cmd_ping(args)
    elif args.command == "load-supabase":
        cmd_load_supabase(args)
    elif args.command == "panel-sync":
        cmd_panel_sync(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
