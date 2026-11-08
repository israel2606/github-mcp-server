"""Consulta las vistas analíticas en Supabase y reporta su estado."""

import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jpojckqnhepiuwefyvdr.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

VIEWS = ["v_aging_cobros", "v_costes_por_obra", "v_margen_por_obra"]


def refresh_views() -> dict:
    """Consulta cada vista analítica y devuelve recuento de filas."""
    if not SUPABASE_KEY:
        raise EnvironmentError("SUPABASE_ANON_KEY no está configurada")
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    results = {}
    for view_name in VIEWS:
        try:
            resp = client.table(view_name).select("*").execute()
            rows = resp.data or []
            results[view_name] = {"ok": True, "detail": f"{len(rows)} filas"}
        except Exception as e:
            results[view_name] = {"ok": False, "error": str(e)}
    return results
