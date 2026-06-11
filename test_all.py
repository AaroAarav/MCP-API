import urllib.request
import json

BASE_URL = "http://localhost:8080/api/v1"

endpoints = [
    ("GET", "/queries/slow?limit=2"),
    ("GET", "/queries/active"),
    ("GET", "/queries/long-running"),
    ("GET", "/queries/temp-spill"),
    ("POST", "/queries/explain", {"query": "SELECT * FROM pg_class LIMIT 1"}),
    ("GET", "/sessions/blocking"),
    ("GET", "/sessions/idle-in-transaction"),
    ("GET", "/sessions/connections"),
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
    ("GET", "/replication/lag"),
    ("GET", "/schema/context")
]

results = {}

for method, path, *body in endpoints:
    url = BASE_URL + path
    try:
        if method == "GET":
            req = urllib.request.Request(url)
        else:
            data = json.dumps(body[0]).encode('utf-8') if body else b"{}"
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            results[path] = res_data
    except Exception as e:
        results[path] = {"error": str(e)}

with open("test_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("Done")
