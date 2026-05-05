import time
import statistics
from core.ping_test import ping_host
from core.helpers import get_quality_label, format_latency


def run_stability_test(host="8.8.8.8", duration=30, interval=1):
    """
    Run a stability test over a period of time.
    Pings the host every `interval` seconds for `duration` seconds.

    host     : target to ping
    duration : how long to run the test in seconds (default 30s)
    interval : time between pings in seconds (default 1s)
    """
    print(f"\nRunning stability test for {duration} seconds...")

    latencies   = []
    errors      = 0
    total       = 0

    start_time  = time.time()

    while time.time() - start_time < duration:
        total += 1
        raw = ping_host(host=host, count=1)

        if raw["results"]:
            latencies.append(raw["results"][0])
            elapsed = round(time.time() - start_time, 1)
            print(f"  [{elapsed}s] Ping: {format_latency(raw['results'][0])}")
        else:
            errors += 1
            elapsed = round(time.time() - start_time, 1)
            print(f"  [{elapsed}s] Ping: Timeout")

        time.sleep(interval)

    return analyze_stability(latencies, errors, total, host, duration)


def analyze_stability(latencies, errors, total, host, duration):
    """
    Analyze stability data and produce a full stability report.
    """
    if not latencies:
        return {
            "success": False,
            "error":   "No successful pings during stability test."
        }

    avg_latency     = round(statistics.mean(latencies), 2)
    min_latency     = round(min(latencies), 2)
    max_latency     = round(max(latencies), 2)
    jitter          = round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0.0
    packet_loss     = round((errors / total) * 100, 1)
    latency_range   = round(max_latency - min_latency, 2)

    # Calculate stability score out of 100
    stability_score = calculate_stability_score(avg_latency, jitter, packet_loss)
    stability_label = get_stability_label(stability_score)
    connection_type = classify_connection(avg_latency, jitter, packet_loss)

    return {
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
        "jitter_quality":   get_quality_label("jitter", jitter),
        "loss_quality":     get_quality_label("packet_loss", packet_loss),
    }


def calculate_stability_score(avg_latency, jitter, packet_loss):
    """
    Calculate a stability score out of 100 based on:
    - Average latency  (40% weight)
    - Jitter           (40% weight)
    - Packet loss      (20% weight)
    """
    # Latency score (40 points)
    if avg_latency <= 20:
        latency_score = 40
    elif avg_latency <= 50:
        latency_score = 30
    elif avg_latency <= 100:
        latency_score = 20
    else:
        latency_score = 10

    # Jitter score (40 points)
    if jitter <= 5:
        jitter_score = 40
    elif jitter <= 10:
        jitter_score = 30
    elif jitter <= 20:
        jitter_score = 20
    else:
        jitter_score = 10

    # Packet loss score (20 points)
    if packet_loss == 0:
        loss_score = 20
    elif packet_loss <= 1:
        loss_score = 15
    elif packet_loss <= 5:
        loss_score = 10
    else:
        loss_score = 0

    return latency_score + jitter_score + loss_score


def get_stability_label(score):
    """Convert stability score to a human readable label"""
    if score >= 90:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    else:
        return "Poor"


def classify_connection(avg_latency, jitter, packet_loss):
    """
    Classify the type of connection based on behavior patterns.
    """
    if avg_latency <= 20 and jitter <= 3 and packet_loss == 0:
        return "Fiber / High-Speed Broadband"
    elif avg_latency <= 50 and jitter <= 10 and packet_loss <= 1:
        return "Cable / Standard Broadband"
    elif avg_latency <= 100 and jitter <= 20:
        return "DSL / Wireless Broadband"
    elif avg_latency > 100 and packet_loss > 2:
        return "Mobile Data / Weak Signal"
    else:
        return "Unknown / Mixed Connection"


def display_stability_results(result):
    """Simple print display for quick testing"""
    if result["success"]:
        print("\n--- Stability Test Results ---")
        print(f"Host             : {result['host']}")
        print(f"Duration         : {result['duration']}s")
        print(f"Total Pings      : {result['total_pings']}")
        print(f"Successful       : {result['successful_pings']}")
        print(f"Failed           : {result['failed_pings']}")
        print(f"Packet Loss      : {result['packet_loss']}%")
        print(f"Min Latency      : {format_latency(result['min_latency'])}")
        print(f"Avg Latency      : {format_latency(result['avg_latency'])}")
        print(f"Max Latency      : {format_latency(result['max_latency'])}")
        print(f"Jitter           : {format_latency(result['jitter'])}")
        print(f"Latency Range    : {format_latency(result['latency_range'])}")
        print(f"Stability Score  : {result['stability_score']}/100")
        print(f"Stability Label  : {result['stability_label']}")
        print(f"Connection Type  : {result['connection_type']}")
    else:
        print(f"\n[ERROR] {result['error']}")


# Quick test
if __name__ == "__main__":
    result = run_stability_test(duration=10)
    display_stability_results(result)