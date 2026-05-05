import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QScrollArea, QProgressBar, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


def make_card(object_name="card"):
    """Create a styled card frame"""
    frame = QFrame()
    frame.setObjectName(object_name)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(8)
    return frame, layout


def make_section_title(text):
    """Create a section title label"""
    label = QLabel(text.upper())
    label.setObjectName("section_title")
    return label


def make_metric_row(key, value="—", value_object_name="metric_value"):
    """Create a key-value metric row"""
    row     = QWidget()
    layout  = QHBoxLayout(row)
    layout.setContentsMargins(0, 2, 0, 2)
    layout.setSpacing(8)

    key_label = QLabel(key)
    key_label.setObjectName("metric_key")
    key_label.setFixedWidth(140)

    val_label = QLabel(value)
    val_label.setObjectName(value_object_name)
    val_label.setWordWrap(True)

    layout.addWidget(key_label)
    layout.addWidget(val_label, 1)

    return row, val_label


def make_divider():
    """Create a horizontal divider line"""
    divider = QFrame()
    divider.setObjectName("divider")
    divider.setFrameShape(QFrame.Shape.HLine)
    return divider


class DashboardWidget(QWidget):
    """
    Main dashboard widget containing all result panels.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        # Outer scroll area
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(14)

        # Build all panels
        self._build_isp_panel()
        self._build_speed_panel()
        self._build_ping_panel()
        self._build_stability_panel()
        self._build_summary_panel()

        self.main_layout.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

    # ── ISP Panel ─────────────────────────────────────────────────
    def _build_isp_panel(self):
        card, layout = make_card("card_accent")
        layout.addWidget(make_section_title("◈  Network Identity"))
        layout.addWidget(make_divider())

        self._isp_rows = {}
        for key, attr in [
            ("IP Address", "isp_ip"),
            ("ISP / Org", "isp_org"),
            ("City", "isp_city"),
            ("Country", "isp_country"),
            ("Timezone", "isp_timezone"),
        ]:
            row, val = make_metric_row(key)
            self._isp_rows[attr] = val
            layout.addWidget(row)

        self.main_layout.addWidget(card)

    # ── Speed Panel ───────────────────────────────────────────────
    def _build_speed_panel(self):
        card, layout = make_card("card")

        layout.addWidget(make_section_title("◈  Speed Test"))
        layout.addWidget(make_divider())

        # Download + Upload side by side
        speed_row = QHBoxLayout()
        speed_row.setSpacing(14)

        # Download
        dl_widget   = QWidget()
        dl_layout   = QVBoxLayout(dl_widget)
        dl_layout.setContentsMargins(0, 0, 0, 0)
        dl_layout.setSpacing(4)

        dl_title    = QLabel("DOWNLOAD")
        dl_title.setObjectName("metric_key")

        self.dl_value = QLabel("—")
        self.dl_value.setObjectName("speed_value")

        self.dl_unit = QLabel("Mbps")
        self.dl_unit.setObjectName("speed_unit")

        self.dl_quality = QLabel("—")
        self.dl_quality.setObjectName("metric_key")

        self.dl_bar = QProgressBar()
        self.dl_bar.setObjectName("download_bar")
        self.dl_bar.setRange(0, 100)
        self.dl_bar.setValue(0)
        self.dl_bar.setTextVisible(False)

        dl_layout.addWidget(dl_title)
        dl_layout.addWidget(self.dl_value)
        dl_layout.addWidget(self.dl_unit)
        dl_layout.addWidget(self.dl_quality)
        dl_layout.addWidget(self.dl_bar)

        # Upload
        ul_widget   = QWidget()
        ul_layout   = QVBoxLayout(ul_widget)
        ul_layout.setContentsMargins(0, 0, 0, 0)
        ul_layout.setSpacing(4)

        ul_title    = QLabel("UPLOAD")
        ul_title.setObjectName("metric_key")

        self.ul_value = QLabel("—")
        self.ul_value.setObjectName("speed_value")
        self.ul_value.setStyleSheet("color: #A57FDB;")

        self.ul_unit = QLabel("Mbps")
        self.ul_unit.setObjectName("speed_unit")

        self.ul_quality = QLabel("—")
        self.ul_quality.setObjectName("metric_key")

        self.ul_bar = QProgressBar()
        self.ul_bar.setObjectName("upload_bar")
        self.ul_bar.setRange(0, 100)
        self.ul_bar.setValue(0)
        self.ul_bar.setTextVisible(False)

        ul_layout.addWidget(ul_title)
        ul_layout.addWidget(self.ul_value)
        ul_layout.addWidget(self.ul_unit)
        ul_layout.addWidget(self.ul_quality)
        ul_layout.addWidget(self.ul_bar)

        speed_row.addWidget(dl_widget)
        speed_row.addWidget(ul_widget)
        layout.addLayout(speed_row)

        layout.addWidget(make_divider())

        # Server info
        _, self.speed_server  = make_metric_row("Server")
        _, self.speed_sponsor = make_metric_row("Sponsor")
        _, self.speed_latency = make_metric_row("Server Latency")

        self._speed_rows = {}
        for key, attr in [
            ("Server",          "speed_server"),
            ("Sponsor",         "speed_sponsor"),
            ("Server Latency",  "speed_latency"),
        ]:
            row, val = make_metric_row(key)
            self._speed_rows[attr] = val
            layout.addWidget(row)

        self.main_layout.addWidget(card)

    # ── Ping Panel ────────────────────────────────────────────────
    def _build_ping_panel(self):
        card, layout = make_card("card_purple")

        layout.addWidget(make_section_title("◈  Ping & Latency"))
        layout.addWidget(make_divider())

        # Big ping value
        ping_center = QHBoxLayout()

        ping_display    = QWidget()
        ping_disp_layout = QVBoxLayout(ping_display)
        ping_disp_layout.setContentsMargins(0, 0, 0, 0)
        ping_disp_layout.setSpacing(2)

        ping_title = QLabel("AVG LATENCY")
        ping_title.setObjectName("metric_key")

        self.ping_big_value = QLabel("—")
        self.ping_big_value.setObjectName("ping_value")

        ping_ms = QLabel("ms")
        ping_ms.setObjectName("speed_unit")

        ping_disp_layout.addWidget(ping_title)
        ping_disp_layout.addWidget(self.ping_big_value)
        ping_disp_layout.addWidget(ping_ms)

        ping_center.addWidget(ping_display)
        ping_center.addStretch()
        layout.addLayout(ping_center)

        layout.addWidget(make_divider())

        self._ping_rows = {}
        for key, attr in [
            ("Min Latency",     "ping_min"),
            ("Max Latency",     "ping_max"),
            ("Jitter",          "ping_jitter"),
            ("Packet Loss",     "ping_loss"),
            ("Ping Quality",    "ping_quality"),
            ("Jitter Quality",  "ping_jitter_quality"),
        ]:
            row, val = make_metric_row(key)
            self._ping_rows[attr] = val
            layout.addWidget(row)

        self.main_layout.addWidget(card)

    # ── Stability Panel ───────────────────────────────────────────
    def _build_stability_panel(self):
        card, layout = make_card("card_yellow")

        layout.addWidget(make_section_title("◈  Connection Stability"))
        layout.addWidget(make_divider())

        # Score display
        score_row = QHBoxLayout()

        score_display   = QWidget()
        score_layout    = QVBoxLayout(score_display)
        score_layout.setContentsMargins(0, 0, 0, 0)
        score_layout.setSpacing(2)

        score_title = QLabel("STABILITY SCORE")
        score_title.setObjectName("metric_key")

        self.score_big_value = QLabel("—")
        self.score_big_value.setObjectName("score_value")

        score_out_of = QLabel("/ 100")
        score_out_of.setObjectName("speed_unit")

        self.stability_bar = QProgressBar()
        self.stability_bar.setObjectName("stability_bar")
        self.stability_bar.setRange(0, 100)
        self.stability_bar.setValue(0)
        self.stability_bar.setTextVisible(False)

        score_layout.addWidget(score_title)
        score_layout.addWidget(self.score_big_value)
        score_layout.addWidget(score_out_of)
        score_layout.addWidget(self.stability_bar)

        score_row.addWidget(score_display)
        score_row.addStretch()
        layout.addLayout(score_row)

        layout.addWidget(make_divider())

        # Live ping log
        live_title = QLabel("LIVE PING LOG")
        live_title.setObjectName("metric_key")
        layout.addWidget(live_title)

        self.live_ping_label = QLabel("Waiting for stability test...")
        self.live_ping_label.setObjectName("metric_key")
        self.live_ping_label.setWordWrap(True)
        layout.addWidget(self.live_ping_label)

        layout.addWidget(make_divider())

        self._stability_rows = {}
        for key, attr in [
            ("Avg Latency",     "stab_avg"),
            ("Jitter",          "stab_jitter"),
            ("Packet Loss",     "stab_loss"),
            ("Latency Range",   "stab_range"),
            ("Connection Type", "stab_type"),
            ("Label",           "stab_label"),
        ]:
            row, val = make_metric_row(key)
            self._stability_rows[attr] = val
            layout.addWidget(row)

        self.main_layout.addWidget(card)

    # ── Summary Panel ─────────────────────────────────────────────
    def _build_summary_panel(self):
        card, layout = make_card("card_green")

        layout.addWidget(make_section_title("◈  Summary"))
        layout.addWidget(make_divider())

        self._summary_rows = {}
        for key, attr in [
            ("ISP",         "sum_isp"),
            ("Ping",        "sum_ping"),
            ("Download",    "sum_download"),
            ("Upload",      "sum_upload"),
            ("Stability",   "sum_stability"),
        ]:
            row, val = make_metric_row(key)
            self._summary_rows[attr] = val
            layout.addWidget(row)

        self.main_layout.addWidget(card)

    # ── Update Methods ────────────────────────────────────────────
    def update_isp(self, result):
        if not result["success"]:
            return
        d = result["data"]
        self._isp_rows["isp_ip"].setText(d["ip"])
        self._isp_rows["isp_org"].setText(d["isp"])
        self._isp_rows["isp_city"].setText(d["city"])
        self._isp_rows["isp_country"].setText(f"{d['country']} — {d['region']}")
        self._isp_rows["isp_timezone"].setText(d["timezone"])
        self._summary_rows["sum_isp"].setText(d["isp"])

    def update_ping(self, result):
        if not result["success"]:
            return
        self.ping_big_value.setText(str(result["avg_latency"]))
        self._ping_rows["ping_min"].setText(f"{result['min_latency']} ms")
        self._ping_rows["ping_max"].setText(f"{result['max_latency']} ms")
        self._ping_rows["ping_jitter"].setText(f"{result['jitter']} ms")
        self._ping_rows["ping_loss"].setText(f"{result['packet_loss']}%")
        self._set_quality(self._ping_rows["ping_quality"], result["ping_quality"])
        self._set_quality(self._ping_rows["ping_jitter_quality"], result["jitter_quality"])
        self._summary_rows["sum_ping"].setText(
            f"{result['avg_latency']} ms — {result['ping_quality']}"
        )

    def update_speed(self, result):
        if not result["success"]:
            return
        self.dl_value.setText(str(result["download_mbps"]))
        self.ul_value.setText(str(result["upload_mbps"]))
        self._set_quality(self.dl_quality, result["download_quality"])
        self._set_quality(self.ul_quality, result["upload_quality"])
        self.dl_bar.setValue(min(int(result["download_mbps"]), 100))
        self.ul_bar.setValue(min(int(result["upload_mbps"]), 100))
        self._speed_rows["speed_server"].setText(
            f"{result['server']['name']}, {result['server']['country']}"
        )
        self._speed_rows["speed_sponsor"].setText(result["server"]["sponsor"])
        self._speed_rows["speed_latency"].setText(f"{result['server']['latency']} ms")
        self._summary_rows["sum_download"].setText(
            f"{result['download_mbps']} Mbps — {result['download_quality']}"
        )
        self._summary_rows["sum_upload"].setText(
            f"{result['upload_mbps']} Mbps — {result['upload_quality']}"
        )

    def update_stability(self, result):
        if not result["success"]:
            return
        self.score_big_value.setText(str(result["stability_score"]))
        self.stability_bar.setValue(result["stability_score"])
        self._stability_rows["stab_avg"].setText(f"{result['avg_latency']} ms")
        self._stability_rows["stab_jitter"].setText(f"{result['jitter']} ms")
        self._stability_rows["stab_loss"].setText(f"{result['packet_loss']}%")
        self._stability_rows["stab_range"].setText(f"{result['latency_range']} ms")
        self._stability_rows["stab_type"].setText(result["connection_type"])
        self._set_quality(self._stability_rows["stab_label"], result["stability_label"])
        self._summary_rows["sum_stability"].setText(
            f"{result['stability_score']}/100 — {result['stability_label']}"
        )

    def update_live_ping(self, latency, elapsed):
        """Update live ping log during stability test"""
        current = self.live_ping_label.text()
        if current == "Waiting for stability test...":
            current = ""
        new_line = f"[{elapsed}s] {latency:.2f} ms"
        lines = current.split("\n") if current else []
        lines.append(new_line)
        # Keep last 8 lines only
        if len(lines) > 8:
            lines = lines[-8:]
        self.live_ping_label.setText("\n".join(lines))

    def _set_quality(self, label, quality):
        """Set quality label text and style"""
        label.setText(quality)
        quality_map = {
            "Excellent": "quality_excellent",
            "Good":      "quality_good",
            "Average":   "quality_average",
            "Fair":      "quality_average",
            "Poor":      "quality_poor",
        }
        label.setObjectName(quality_map.get(quality, "metric_value"))
        label.style().unpolish(label)
        label.style().polish(label)

    def reset(self):
        """Reset all displayed values to default"""
        self._isp_rows["isp_ip"].setText("—")
        self._isp_rows["isp_org"].setText("—")
        self._isp_rows["isp_city"].setText("—")
        self._isp_rows["isp_country"].setText("—")
        self._isp_rows["isp_timezone"].setText("—")
        self.dl_value.setText("—")
        self.ul_value.setText("—")
        self.dl_bar.setValue(0)
        self.ul_bar.setValue(0)
        self.ping_big_value.setText("—")
        self.score_big_value.setText("—")
        self.stability_bar.setValue(0)
        self.live_ping_label.setText("Waiting for stability test...")
        for rows in [self._ping_rows, self._speed_rows,
                     self._stability_rows, self._summary_rows]:
            for val in rows.values():
                val.setText("—")