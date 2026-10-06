"""Holded API extractor — paginación automática con rate-limit."""

import os
import time
import requests

BASE_URL = "https://api.holded.com/api"

EMPRESAS = {
    "TESELA_GESTION": os.getenv("HOLDED_API_KEY_TESELA_GESTION"),
    "ISELA":          os.getenv("HOLDED_API_KEY_ISELA"),
    "PADAMAIS":       os.getenv("HOLDED_API_KEY_PADAMAIS"),
    "TESELAB":        os.getenv("HOLDED_API_KEY_TESELAB"),
    "EMPRESA5":       os.getenv("HOLDED_API_KEY_EMPRESA5"),
}

ENDPOINTS = {
    "contacts":  "contacts/v1/contacts",
    "invoices":  "invoicing/v1/invoices",
    "bills":     "invoicing/v1/bills",
    "estimates": "invoicing/v1/estimates",
    "waybills":  "invoicing/v1/waybills",
    "products":  "invoicing/v1/products",
    "projects":  "projects/v1/projects",
    "expenses":  "expenses/v1/expenses",
    "receipts":  "treasury/v1/receipts",
    "payments":  "treasury/v1/payments",
    "banks":     "treasury/v1/banks",
    "accounts":  "accounting/v1/accounts",
    "ledger":    "accounting/v1/ledger",
}


def holded_get(api_key: str, endpoint: str, params: dict = None) -> list:
    """Pagina automáticamente hasta agotar resultados. Respeta rate limit."""
    if params is None:
        params = {}
    headers = {"key": api_key, "Accept": "application/json"}
    results = []
    page = 1
    while True:
        p = {**params, "page": page, "limit": 100}
        try:
            r = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=p, timeout=30)
        except requests.RequestException as e:
            raise RuntimeError(f"Error de red en {endpoint}: {e}") from e

        if r.status_code == 401:
            raise PermissionError(f"API key inválida para endpoint {endpoint}")
        if r.status_code == 429:
            print("  ⚠ Rate limit — esperando 60s...")
            time.sleep(60)
            continue
        if r.status_code >= 500:
            # retry x3 con backoff exponencial
            for attempt in range(3):
                wait = 2 ** (attempt + 1)
                print(f"  ⚠ Error {r.status_code} en {endpoint}, reintento {attempt+1}/3 en {wait}s...")
                time.sleep(wait)
                r = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=p, timeout=30)
                if r.status_code < 500:
                    break
            else:
                r.raise_for_status()

        r.raise_for_status()
        data = r.json()
        if not data:
            break
        if isinstance(data, list):
            results.extend(data)
            if len(data) < 100:
                break
        else:
            results.append(data)
            break
        page += 1
        time.sleep(0.3)
    return results


def ping_sociedad(sociedad: str, api_key: str) -> dict:
    """Verifica conectividad sin cargar datos completos."""
    try:
        contacts = holded_get(api_key, ENDPOINTS["contacts"], {"limit": 1, "page": 1})
        return {"ok": True, "sociedad": sociedad, "sample_count": len(contacts)}
    except PermissionError as e:
        return {"ok": False, "sociedad": sociedad, "error": str(e)}
    except Exception as e:
        return {"ok": False, "sociedad": sociedad, "error": str(e)}


def sync_sociedad(sociedad: str, api_key: str) -> dict:
    """Extrae todos los endpoints para una sociedad."""
    print(f"\n→ Sincronizando {sociedad}...")
    data = {}
    for name, endpoint in ENDPOINTS.items():
        try:
            records = holded_get(api_key, endpoint)
            data[name] = records
            print(f"  ✓ {name}: {len(records)} registros")
        except PermissionError as e:
            print(f"  ✗ {name}: {e}")
            data[name] = []
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            data[name] = []
    return data
