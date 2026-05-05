import speedtest
from core.helpers import format_speed, get_quality_label, get_timestamp


def get_best_server(st):
    """
    Find the best speedtest server based on latency.
    Returns server info dict.
    """
    print("  Finding best server...")
    st.get_best_server()
    server = st.results.server
    return {
        "name":     server.get("name", "N/A"),
        "country":  server.get("country", "N/A"),
        "sponsor":  server.get("sponsor", "N/A"),
        "latency":  round(server.get("latency", 0), 2),
    }


def run_download_test(st):
    """
    Run download speed test.
    Returns speed in bits per second.
    """
    print("  Testing download speed...")
    download_bps = st.download()
    return download_bps


def run_upload_test(st):
    """
    Run upload speed test.
    Returns speed in bits per second.
    """
    print("  Testing upload speed...")
    upload_bps = st.upload()
    return upload_bps


def run_speed_test():
    """
    Main function — runs full speed test including
    server selection, download and upload.
    Returns complete result dict.
    """
    try:
        print("\nInitializing speed test...")
        st = speedtest.Speedtest()

        # Get best server
        server      = get_best_server(st)

        # Run download test
        download_bps = run_download_test(st)

        # Run upload test
        upload_bps   = run_upload_test(st)

        # Convert to Mbps
        download_mbps = round(download_bps / 1_000_000, 2)
        upload_mbps   = round(upload_bps   / 1_000_000, 2)

        return {
            "success":          True,
            "timestamp":        get_timestamp(),
            "server":           server,
            "download_bps":     download_bps,
            "upload_bps":       upload_bps,
            "download_mbps":    download_mbps,
            "upload_mbps":      upload_mbps,
            "download_quality": get_quality_label("download", download_mbps),
            "upload_quality":   get_quality_label("upload",   upload_mbps),
        }

    except speedtest.ConfigFetchError:
        return {
            "success": False,
            "error":   "Failed to fetch speedtest config. Check your internet connection."
        }
    except speedtest.NoMatchedServers:
        return {
            "success": False,
            "error":   "No speedtest servers found nearby."
        }
    except speedtest.SpeedtestBestServerFailure:
        return {
            "success": False,
            "error":   "Could not find best server. Try again."
        }
    except Exception as e:
        return {
            "success": False,
            "error":   f"Speed test failed: {str(e)}"
        }


def display_speed_results(result):
    """Simple print display for quick testing"""
    if result["success"]:
        server = result["server"]
        print("\n--- Speed Test Results ---")
        print(f"Timestamp        : {result['timestamp']}")
        print(f"Server           : {server['name']}, {server['country']}")
        print(f"Sponsor          : {server['sponsor']}")
        print(f"Server Latency   : {server['latency']} ms")
        print(f"Download Speed   : {format_speed(result['download_bps'])}")
        print(f"Upload Speed     : {format_speed(result['upload_bps'])}")
        print(f"Download Quality : {result['download_quality']}")
        print(f"Upload Quality   : {result['upload_quality']}")
    else:
        print(f"\n[ERROR] {result['error']}")


# Quick test
if __name__ == "__main__":
    result = run_speed_test()
    display_speed_results(result)