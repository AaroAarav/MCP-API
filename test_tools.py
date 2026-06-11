import urllib.request
import json
import urllib.error

BASE_URL = "http://localhost:8080/api/v1"

endpoints = [
    ("GET", "/queries/slow?limit=10&order_by=total_time"),
    ("GET", "/queries/active"),
    ("GET", "/queries/long-running?min_seconds=30"),
    ("GET", "/queries/temp-spill?limit=10"),
    ("POST", "/queries/explain", {"query": "SELECT 1"}),
    ("GET", "/sessions/blocking"),
    ("GET", "/sessions/idle-in-transaction?min_seconds=60"),
    ("GET", "/sessions/connections"),
    ("POST", "/sessions/999999/cancel", {"reason": "test"}),
    ("POST", "/sessions/999999/terminate", {"reason": "test", "confirm": True}),
    ("GET", "/cache/hit-rates"),
    ("GET", "/indexes/missing"),
    ("GET", "/indexes/unused"),
    ("GET", "/indexes/duplicate"),
    ("GET", "/indexes/bloated"),
    ("GET", "/indexes/unindexed-fks"),
    ("GET", "/tables/bloat"),
    ("GET", "/tables/vacuum-status"),
    ("GET", "/tables/statistics-staleness"),
    ("GET", "/tables/vacuum-progress"),
    ("POST", "/tables/pg_class/vacuum", {"confirm": True}),
    ("POST", "/tables/pg_class/analyze", {"confirm": True}),
    ("POST", "/indexes/pg_class_oid_index/reindex", {"confirm": True}),
    ("GET", "/replication/lag"),
    ("GET", "/schema/context")
]

print("Starting tool tests against the Live API...")

for item in endpoints:
    method = item[0]
    path = item[1]
    body = item[2] if len(item) > 2 else None
    
    url = BASE_URL + path
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    data = None
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        
    try:
        with urllib.request.urlopen(req, data=data) as response:
            status = response.getcode()
            print(f"[OK] {method} {path} -> {status}")
    except urllib.error.HTTPError as e:
        res = e.read().decode()
        # 404 or 400 is expected for canceling invalid PIDs or bad test data, but 500 is a crash
        if e.code == 500:
            print(f"[FAIL] {method} {path} -> {e.code}: {res}")
        else:
            print(f"[{e.code}] {method} {path} -> {res.strip()}")
    except Exception as e:
        print(f"[ERROR] {method} {path} -> {e}")

print("Done.")
