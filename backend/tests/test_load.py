"""
Load Testing Script: 100 Simultaneous Requests.
Verifies performance and stability under concurrent user load (<2s response time target).
"""

import time
import concurrent.futures
from fastapi.testclient import TestClient
from backend.app.main import app

def send_request(user_index: int):
    client = TestClient(app)
    start = time.time()
    res = client.post("/api/chat", json={
        "query": "Quels sont les horaires de la bibliothèque universitaire ?",
        "session_id": f"load_session_{user_index}",
        "client_id": f"load_user_{user_index}"
    })
    elapsed = time.time() - start
    return res.status_code, elapsed

def test_load_100_simultaneous_users():
    total_users = 100
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(send_request, i) for i in range(total_users)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    status_codes = [r[0] for r in results]
    latencies = [r[1] for r in results]

    assert all(code == 200 for code in status_codes), "All concurrent requests should return 200 OK"
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    print(f"\n[Load Test Result] 100 users - Avg: {avg_latency*1000:.1f}ms | Max: {max_latency*1000:.1f}ms")
    assert avg_latency < 2.0, f"Average latency must be < 2 seconds, got {avg_latency:.2f}s"
