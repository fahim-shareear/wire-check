import ping3
import statistics
from core.helpers import format_latency, get_quality_label

# ping3 needs root/admin on some systems
ping3.EXCEPTIONS = True


def ping_host(host="8.8.8.8", count=10):
    """
    Ping a host multiple times and collect latency results.
    Returns list of response times in milliseconds.

    host  : target to ping (default Google DNS)
    count : how many ping attempts to make
    """
    results = []
    errors = 0

    for i in range(count):
        try:
            response_time = ping3.ping(host, timeout=2, unit="ms")

            if response_time is None:
                errors += 1
            else:
                results.append(round(response_time, 2))

        except Exception:
            errors += 1

    return {
        "host": host,
        "count": count,
        "results": results,
        "errors": errors,
    }


def analyze_ping(ping_data):
    """
    Analyze raw ping results and calculate:
    - min, max, average latency
    - jitter (standard deviation)
    - packet loss percentage
    """
    results = ping_data["results"]
    count = ping_data["count"]
    errors = ping_data["errors"]

    if not results:
        return {
            "success": False,
            "error": "All ping attempts failed. Check your connection."
        }

    avg_latency = round(statistics.mean(results), 2)
    min_latency = round(min(results), 2)
    max_latency = round(max(results), 2)
    jitter = round(statistics.stdev(results), 2) if len(results) > 1 else 0.0
    packet_loss = round((errors / count) * 100, 1)

    return {
        "success": True,
        "host": ping_data["host"],
        "packets_sent": count,
        "packets_received": len(results),
        "packet_loss": packet_loss,
        "min_latency": min_latency,
        "max_latency": max_latency,
        "avg_latency": avg_latency,
        "jitter": jitter,
        "ping_quality": get_quality_label("ping", avg_latency),
        "jitter_quality": get_quality_label("jitter", jitter),
        "loss_quality": get_quality_label("packet_loss", packet_loss),
    }


def run_ping_test(host="8.8.8.8", count=10):
    """Main function — runs ping and returns full analysis"""
    raw = ping_host(host, count)
    return analyze_ping(raw)


def display_ping_results(ping_result):
    """Simple print display for quick testing"""
    if ping_result["success"]:
        print("\n--- Ping & Latency Test ---")
        print(f"Host             : {ping_result['host']}")
        print(f"Packets Sent     : {ping_result['packets_sent']}")
        print(f"Packets Received : {ping_result['packets_received']}")
        print(f"Packet Loss      : {ping_result['packet_loss']}%")
        print(f"Min Latency      : {format_latency(ping_result['min_latency'])}")
        print(f"Avg Latency      : {format_latency(ping_result['avg_latency'])}")
        print(f"Max Latency      : {format_latency(ping_result['max_latency'])}")
        print(f"Jitter           : {format_latency(ping_result['jitter'])}")
        print(f"Ping Quality     : {ping_result['ping_quality']}")
        print(f"Jitter Quality   : {ping_result['jitter_quality']}")
        print(f"Loss Quality     : {ping_result['loss_quality']}")
    else:
        print(f"\n[ERROR] {ping_result['error']}")


# Quick test
if __name__ == "__main__":
    result = run_ping_test()
    display_ping_results(result)