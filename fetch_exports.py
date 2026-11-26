"""
Runs SQL files against the Coinbase CDP SQL API and saves each result as CSV in data/.

Auth: CDP Secret API key (cdp_api_key.json downloaded from the CDP portal), used to sign
a short-lived JWT for each request. The key never leaves your machine.

Install once:
    pip install cdp-sdk

Usage:
    py fetch_exports.py sql/q6a_received_per_host_day.sql sql/q6b_sent_per_host_day.sql

Results are written to data/<query_name>.csv

NEVER commit cdp_api_key.json (it is listed in .gitignore).
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
        sys.exit(f"Unexpected fields in {KEY_FILE}: {list(k.keys())}")
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
        sys.exit(f"Error {e.code}: {e.read().decode()[:500]}")
    print(f"  {data.get('metadata', {}).get('rowCount')} rows")
    return data["result"]


def main():
    key_id, secret = load_key()
    for path in sys.argv[1:]:
        print(path)
        rows = run(open(path, encoding="utf-8").read(), key_id, secret)
        os.makedirs("data", exist_ok=True)
        out = os.path.join("data", os.path.splitext(os.path.basename(path))[0] + ".csv")
        with open(out, "w", newline="", encoding="utf-8") as f:
            if rows:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
        print(f"  -> {out}")


if __name__ == "__main__":
    main()
