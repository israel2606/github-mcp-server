#!/usr/bin/env python3
"""
tesela-erp CLI — comandos holded-ping, load-supabase, panel-sync.

Uso:
    python -m holded.cli holded-ping
    python -m holded.cli load-supabase
    python -m holded.cli panel-sync
    python -m holded.cli load-supabase --sociedad TESELA_GESTION
"""

import sys
import argparse
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
    target = args.sociedad.upper() if args.sociedad else None
    for sociedad, key in EMPRESAS.items():
        if target and sociedad != target:
            continue
        if not key:
            print(f"  ✗ {sociedad}: sin API key, saltando")
            continue
        data = sync_sociedad(sociedad, key)
        counts = load_sociedad(sociedad, data)
        print(
            f"  ✓ {sociedad}: "
            f"{counts['contacts']} contactos, "
            f"{counts['invoices']} ventas, "
            f"{counts['bills']} compras, "
            f"{counts['projects']} proyectos"
        )
    print("─" * 50)


def cmd_panel_sync(args):
    print("─" * 50)
    print("tesela-erp panel-sync")
    print("─" * 50)
    print("Recalculando vistas materializadas...")
    results = refresh_views()
    for view, info in results.items():
        if info.get("ok"):
            detail = info.get("detail", "")
            print(f"  ✓ {view}: {detail}")
        else:
            print(f"  ✗ {view}: {info.get('error')}")
    print("─" * 50)


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
