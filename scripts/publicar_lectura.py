#!/usr/bin/env python3
"""Publica una lectura previamente aprobada; nunca genera contenido ni sobrescribe."""
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

BASE = "https://lszjnrjgbhsfrdvhhfvg.supabase.co"
FIELDS = ("fecha", "titulo", "referencia", "texto_biblico", "traduccion",
          "contexto", "reflexion", "oracion", "practica", "frase", "etiquetas")
TZ = ZoneInfo("America/Costa_Rica")


def request(method, path, key, payload=None, extra=None):
    headers = {"apikey": key, "Authorization": "Bearer " + key,
               "Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    headers.update(extra or {})
    req = urllib.request.Request(
        BASE + "/rest/v1/" + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None,
        headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode("utf-8")
        return json.loads(data) if data else None


def main():
    today = dt.datetime.now(TZ).date()
    target = today + dt.timedelta(days=1)
    if os.environ.get("TARGET_DATE"):
        target = dt.date.fromisoformat(os.environ["TARGET_DATE"])
    print("Costa Rica:", today, "| Fecha objetivo:", target)
    queue = json.loads(pathlib.Path("lecturas-programadas.json").read_text(encoding="utf-8"))
    matching = [r for r in queue if r.get("fecha") == target.isoformat()]
    if len(matching) != 1:
        raise RuntimeError(f"Se requiere exactamente una lectura preparada para {target}; encontradas: {len(matching)}")
    row = matching[0]
    for field in FIELDS:
        value = row.get(field)
        if not value or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"Campo obligatorio vacío: {field}")
    if row["traduccion"].strip().lower().replace("-", "") not in ("rv1909", "reinavalera 1909", "reina valera 1909"):
        raise ValueError("Solo se permite texto verificado Reina-Valera 1909")
    if not isinstance(row["etiquetas"], list) or not all(isinstance(t, str) and t.strip() for t in row["etiquetas"]):
        raise ValueError("Etiquetas inválidas")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not key:
        raise RuntimeError("Falta configurar GitHub Secret SUPABASE_SERVICE_ROLE_KEY")
    query = urllib.parse.urlencode({"fecha": "eq." + target.isoformat(), "select": "id,fecha,publicada"})
    existing = request("GET", "lecturas?" + query, key)
    if existing:
        if len(existing) != 1:
            raise RuntimeError("Hay múltiples registros para esta fecha; intervención manual requerida")
        if not existing[0]["publicada"]:
            raise RuntimeError("La fecha ya existe pero no está publicada; no se sobrescribe")
        print("Ya publicada; no se modifica:", target)
        return
    payload = {field: row[field] for field in FIELDS}
    payload["publicada"] = True
    try:
        result = request("POST", "lecturas?on_conflict=fecha", key, [payload],
                         {"Prefer": "resolution=ignore-duplicates,return=representation"})
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Error Supabase: " + exc.read().decode("utf-8")[:500]) from exc
    verified = request("GET", "lecturas?" + query, key)
    if len(verified) != 1 or not verified[0]["publicada"]:
        raise RuntimeError("No se pudo verificar la publicación")
    print("Lectura publicada y verificada:", target, "| Inserciones:", len(result or []))
    print("El audio se gestiona por separado; este proceso no asegura su generación.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
