"""
Lance les requêtes SQL (fichiers .sql) sur l'API SQL de Coinbase CDP
et enregistre chaque résultat en CSV.

Authentification : la Secret API key (fichier cdp_api_key.json téléchargé depuis le portail CDP),
utilisée pour signer un jeton JWT à chaque requête. La clé ne quitte jamais ton PC.

Installation (une seule fois) :
    py -m pip install cdp-sdk

Usage :
    py fetch_exports.py test.sql
    py fetch_exports.py q6a_recu_par_host_jour.sql q6b_envoye_par_host_jour.sql

NE JAMAIS publier cdp_api_key.json (il est listé dans .gitignore).
"""
import csv
import json
import os
import sys
import urllib.error
import urllib.request

from cdp.auth.utils.jwt import JwtOptions, generate_jwt

HOST = "api.cdp.coinbase.com"
PATH = "/platform/v2/data/query/run"
KEY_FILE = "cdp_api_key.json"


def load_key():
    k = json.load(open(KEY_FILE, encoding="utf-8"))
    key_id = k.get("id") or k.get("name") or k.get("keyId")
    secret = k.get("privateKey") or k.get("secret")
    if not key_id or not secret:
        sys.exit(f"Champs inattendus dans {KEY_FILE} : {list(k.keys())}")
    return key_id, secret


def run(sql: str, key_id: str, secret: str) -> list[dict]:
    token = generate_jwt(JwtOptions(
        api_key_id=key_id,
        api_key_secret=secret,
        request_method="POST",
        request_host=HOST,
        request_path=PATH,
        expires_in=120,
    ))
    req = urllib.request.Request(
        f"https://{HOST}{PATH}",
        data=json.dumps({"sql": sql}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Erreur {e.code} : {e.read().decode()[:500]}")
    print(f"  {data.get('metadata', {}).get('rowCount')} lignes")
    return data["result"]


def main():
    key_id, secret = load_key()
    for path in sys.argv[1:]:
        print(path)
        rows = run(open(path, encoding="utf-8").read(), key_id, secret)
        out = os.path.splitext(path)[0] + ".csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            if rows:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
        print(f"  -> {out}")


if __name__ == "__main__":
    main()
