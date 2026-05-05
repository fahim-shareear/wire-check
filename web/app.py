import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import threading
from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS

from core.isp_info import get_isp_info
from core.ping_test import run_ping_test
from core.speed_test import run_speed_test
from core.stability import (
    calculate_stability_score,
    get_stability_label,
    classify_connection
)

app = Flask(__name__)
CORS(app)

# ── Routes ─────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/isp")
def api_isp():
    result = get_isp_info()
    return jsonify(result)


@app.route("/api/ping")
def api_ping():
    result = run_ping_test(count=10)
    return jsonify(result)


@app.route("/api/speed")
def api_speed():
    result = run_speed_test()
    return jsonify(result)


@app.route("/api/run")
def api_run():
    """
    Main SSE endpoint — runs all tests and streams
    live progress events to the browser.
    """
    def generate():
        def send(event, data):
            return f"event: {event}\ndata: {json.dumps(data)}\n\n"

        # ── Stage 1 — ISP ─────────────────────────────────
        yield send("progress", {"percent": 5, "message": "Fetching network identity..."})
        isp = get_isp_info()
        yield send("isp", isp)
        yield send("progress", {"percent": 15, "message": "Network identity retrieved."})

        # ── Stage 2 — Ping ────────────────────────────────
        yield send("progress", {"percent": 20, "message": "Running ping test..."})
        ping = run_ping_test(count=10)
        yield send("ping", ping)
        yield send("progress", {"percent": 35, "message": "Ping test complete."})

        # ── Stage 3 — Speed ───────────────────────────────
        yield send("progress", {"percent": 40, "message": "Finding best server..."})
        speed = run_speed_test()
        yield send("speed", speed)
        yield send("progress", {"percent": 70, "message": "Speed test complete."})

        # ── Stage 4 — Stability ───────────────────────────
        yield send("progress", {"percent": 75, "message": "Running stability test..."})

        import time
        import statistics
        import ping3

        host        = "8.8.8.8"
        duration    = 30
        interval    = 1
        latencies   = []
        errors      = 0
        total       = 0
        start_time  = time.time()

        while time.time() - start_time < duration:
            total += 1
            try:
                response = ping3.ping(host, timeout=1, unit="ms")
                elapsed  = int(time.time() - start_time)

                if response is None:
                    errors += 1
                    yield send("stability_ping", {
                        "latency": 0,
                        "elapsed": elapsed,
                        "timeout": True
                    })
                else:
                    latency = round(response, 2)
                    latencies.append(latency)
                    yield send("stability_ping", {
                        "latency": latency,
                        "elapsed": elapsed,
                        "timeout": False
                    })

            except Exception:
                errors += 1

            time.sleep(interval)

        # Build stability result
        if latencies:
            avg_latency     = round(statistics.mean(latencies), 2)
            min_latency     = round(min(latencies), 2)
            max_latency     = round(max(latencies), 2)
            jitter          = round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0.0
            packet_loss     = round((errors / total) * 100, 1)
            latency_range   = round(max_latency - min_latency, 2)
            stability_score = calculate_stability_score(avg_latency, jitter, packet_loss)
            stability_label = get_stability_label(stability_score)
            connection_type = classify_connection(avg_latency, jitter, packet_loss)

            stability = {
                "success":          True,
                "host":             host,
                "duration":         duration,
                "total_pings":      total,
                "successful_pings": len(latencies),
                "failed_pings":     errors,
                "packet_loss":      packet_loss,
                "min_latency":      min_latency,
                "max_latency":      max_latency,
                "avg_latency":      avg_latency,
                "jitter":           jitter,
                "latency_range":    latency_range,
                "stability_score":  stability_score,
                "stability_label":  stability_label,
                "connection_type":  connection_type,
            }
        else:
            stability = {
                "success": False,
                "error":   "No successful pings during stability test."
            }

        yield send("stability", stability)
        yield send("progress", {"percent": 100, "message": "All tests complete."})
        yield send("done", {"message": "All tests complete."})

    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)