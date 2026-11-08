"""Carga datos extraídos de Holded en Supabase vía upsert."""

import os
from datetime import datetime
from zoneinfo import ZoneInfo
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jpojckqnhepiuwefyvdr.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")  # anon key — nunca service_role en código


def _client() -> Client:
    if not SUPABASE_KEY:
        raise EnvironmentError("SUPABASE_ANON_KEY no está configurada")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _today() -> str:
    return datetime.utcnow().isoformat()


# ---------------------------------------------------------------------------
# Funciones de normalización: extraen campos conocidos + guardan raw_json
# ---------------------------------------------------------------------------

def _normalize_contact(sociedad: str, row: dict) -> dict:
    return {
        "sociedad":        sociedad,
        "holded_id":       str(row.get("id", "")),
        "tipo":            row.get("type"),
        "nombre":          row.get("name"),
        "nif":             row.get("vatnumber") or row.get("code"),
        "email":           row.get("email"),
        "saldo_pendiente": row.get("pending"),
        "raw_json":        row,
        "synced_at":       _today(),
    }


def _normalize_invoice(sociedad: str, row: dict) -> dict:
    # Holded puede devolver contactId o contact según la versión del endpoint.
    # pending o paymentsPending según el tipo de documento.
    return {
        "sociedad":         sociedad,
        "holded_id":        str(row.get("id", "")),
        "numero":           row.get("docNumber") or row.get("number"),
        "fecha":            _ts_to_date(row.get("date")),
        "fecha_vencimiento": _ts_to_date(row.get("dueDate")),
        "contact_id":       str(row.get("contactId") or row.get("contact") or ""),
        "contact_nombre":   row.get("contactName"),
        "base_imponible":   row.get("subtotal"),
        "iva":              row.get("tax"),
        "total":            row.get("total"),
        "pendiente":        row.get("pending") if row.get("pending") is not None else row.get("paymentsPending"),
        "estado":           _map_status(row.get("status")),
        "project_id":       str(row.get("projectId", "")) or None,
        "raw_json":         row,
        "synced_at":        _today(),
    }


def _normalize_bill(sociedad: str, row: dict) -> dict:
    return {
        "sociedad":          sociedad,
        "holded_id":         str(row.get("id", "")),
        "numero":            row.get("docNumber") or row.get("number"),
        "fecha":             _ts_to_date(row.get("date")),
        "fecha_vencimiento": _ts_to_date(row.get("dueDate")),
        "proveedor_id":      str(row.get("contactId") or row.get("contact") or ""),
        "proveedor_nombre":  row.get("contactName"),
        "base_imponible":    row.get("subtotal"),
        "iva":               row.get("tax"),
        "total":             row.get("total"),
        "pendiente":         row.get("pending") if row.get("pending") is not None else row.get("paymentsPending"),
        "estado":            _map_status(row.get("status")),
        "project_id":        str(row.get("projectId", "")) or None,
        "cuenta_contable":   row.get("account"),
        "raw_json":          row,
        "synced_at":         _today(),
    }


def _normalize_project(sociedad: str, row: dict) -> dict:
    return {
        "sociedad":         sociedad,
        "holded_id":        str(row.get("id", "")),
        "codigo":           row.get("code") or row.get("ref"),
        "nombre":           row.get("name"),
        "estado":           row.get("status"),
        "fecha_inicio":     _ts_to_date(row.get("startDate")),
        "fecha_fin":        _ts_to_date(row.get("endDate")),
        "presupuesto":      row.get("budget"),
        "coste_acumulado":  row.get("cost"),
        "raw_json":         row,
        "synced_at":        _today(),
    }


_MADRID = ZoneInfo("Europe/Madrid")

# Holded devuelve status como entero en documentos de facturación.
_HOLDED_STATUS_MAP = {0: "pending", 1: "paid", 2: "partial", 3: "cancelled"}


def _ts_to_date(value) -> str | None:
    """Convierte timestamp Unix a string ISO date en zona Europe/Madrid, o None."""
    if not value:
        return None
    try:
        return datetime.fromtimestamp(int(value), _MADRID).date().isoformat()
    except Exception:
        return None


def _map_status(raw) -> str | None:
    """Normaliza el campo status de Holded (entero o string) a string."""
    if isinstance(raw, int):
        return _HOLDED_STATUS_MAP.get(raw)
    return raw


# ---------------------------------------------------------------------------
# Upsert functions
# ---------------------------------------------------------------------------

def upsert_contacts(sociedad: str, rows: list) -> int:
    if not rows:
        return 0
    client = _client()
    records = [_normalize_contact(sociedad, r) for r in rows]
    client.table("holded_contacts").upsert(records, on_conflict="sociedad,holded_id").execute()
    return len(records)


def upsert_invoices(sociedad: str, rows: list) -> int:
    if not rows:
        return 0
    client = _client()
    records = [_normalize_invoice(sociedad, r) for r in rows]
    client.table("holded_invoices").upsert(records, on_conflict="sociedad,holded_id").execute()
    return len(records)


def upsert_bills(sociedad: str, rows: list) -> int:
    if not rows:
        return 0
    client = _client()
    records = [_normalize_bill(sociedad, r) for r in rows]
    client.table("holded_bills").upsert(records, on_conflict="sociedad,holded_id").execute()
    return len(records)


def upsert_projects(sociedad: str, rows: list) -> int:
    if not rows:
        return 0
    client = _client()
    records = [_normalize_project(sociedad, r) for r in rows]
    client.table("holded_projects").upsert(records, on_conflict="sociedad,holded_id").execute()
    return len(records)


def load_sociedad(sociedad: str, data: dict) -> dict:
    """Carga todos los datos de una sociedad en Supabase."""
    counts = {}
    counts["contacts"] = upsert_contacts(sociedad, data.get("contacts", []))
    counts["invoices"] = upsert_invoices(sociedad, data.get("invoices", []))
    counts["bills"]    = upsert_bills(sociedad, data.get("bills", []))
    counts["projects"] = upsert_projects(sociedad, data.get("projects", []))
    return counts
