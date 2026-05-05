import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import QThread, pyqtSignal
from core.isp_info import get_isp_info
from core.ping_test import run_ping_test
from core.speed_test import run_speed_test
from core.stability import run_stability_test


class TestWorker(QThread):
    """
    Background worker that runs all network tests.
    Emits signals to update the UI in real time.
    """

    # ── Signals ───────────────────────────────────────────────
    # Progress signals
    progress_updated    = pyqtSignal(int, str)      # (percent, status message)
    stage_updated       = pyqtSignal(str)           # current stage name

    # Result signals — one per test
    isp_result          = pyqtSignal(dict)
    ping_result         = pyqtSignal(dict)
    speed_result        = pyqtSignal(dict)
    stability_result    = pyqtSignal(dict)

    # Stability live ping signal
    stability_ping      = pyqtSignal(float, int)    # (latency_ms, elapsed_seconds)

    # Completion signals
    all_done            = pyqtSignal()
    error_occurred      = pyqtSignal(str)

    def __init__(self, stability_duration=30):
        super().__init__()
        self.stability_duration = stability_duration
        self._is_running        = True

    def stop(self):
        """Gracefully stop the worker"""
        self._is_running = False

    def run(self):
        """
        Main thread execution.
        Runs all tests in sequence and emits signals.
        """
        try:
            # ── Stage 1 — ISP Info ─────────────────────────
            if not self._is_running:
                return

            self.stage_updated.emit("ISP_INFO")
            self.progress_updated.emit(5, "Fetching network identity...")

            isp = get_isp_info()
            self.isp_result.emit(isp)
            self.progress_updated.emit(15, "Network identity retrieved.")

            # ── Stage 2 — Ping Test ────────────────────────
            if not self._is_running:
                return

            self.stage_updated.emit("PING")
            self.progress_updated.emit(20, "Running ping test...")

            ping = run_ping_test(count=10)
            self.ping_result.emit(ping)
            self.progress_updated.emit(35, "Ping test complete.")

            # ── Stage 3 — Speed Test ───────────────────────
            if not self._is_running:
                return

            self.stage_updated.emit("SPEED")
            self.progress_updated.emit(40, "Finding best server...")

            speed = run_speed_test()
            self.speed_result.emit(speed)
            self.progress_updated.emit(70, "Speed test complete.")

            # ── Stage 4 — Stability Test ───────────────────
            if not self._is_running:
                return

            self.stage_updated.emit("STABILITY")
            self.progress_updated.emit(75, "Running stability test...")

            stability = self._run_stability_with_signals()
            self.stability_result.emit(stability)
            self.progress_updated.emit(100, "All tests complete.")

            # ── Done ───────────────────────────────────────
            self.stage_updated.emit("DONE")
            self.all_done.emit()

        except Exception as e:
            self.error_occurred.emit(str(e))

    def _run_stability_with_signals(self):
        """
        Custom stability runner that emits live ping
        signals so the UI can update in real time.
        """
        import time
        import statistics
        from core.ping_test import ping_host
        from core.helpers import get_quality_label

        host        = "8.8.8.8"
        duration    = self.stability_duration
        interval    = 1

        latencies   = []
        errors      = 0
        total       = 0
        start_time  = time.time()
        while time.time() - start_time < duration:
            if not self._is_running:
                break

            total += 1

            # Use short timeout so stop responds quickly
            try:
                import ping3
                response = ping3.ping(host, timeout=1, unit="ms")
                elapsed = int(time.time() - start_time)

                if response is None:
                    errors += 1
                    self.stability_ping.emit(0.0, elapsed)
                else:
                    latency = round(response, 2)
                    latencies.append(latency)
                    self.stability_ping.emit(latency, elapsed)

            except Exception:
                errors += 1

            # Check stop flag between pings
            for _ in range(10):
                if not self._is_running:
                    break
                time.sleep(0.1)

        # Build result manually
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

        from core.stability import calculate_stability_score, get_stability_label, classify_connection
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