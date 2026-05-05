import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QFont, QIcon

from gui.worker import TestWorker
from gui.widgets.dashboard import DashboardWidget


class MainWindow(QMainWindow):
    """
    Main application window for wire-test.
    """

    def __init__(self):
        super().__init__()
        self.worker = None
        self._load_stylesheet()
        self._build_ui()
        self.setWindowTitle("wire-test — Network Analyzer")
        self.setMinimumSize(720, 820)
        self.resize(820, 900)

    def _load_stylesheet(self):
        """Load QSS dark theme"""
        qss_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets", "style.qss"
        )
        if os.path.exists(qss_path):
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())

    def _build_ui(self):
        """Build the full UI layout"""
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Header
        root_layout.addWidget(self._build_header())

        # Progress bar + status
        root_layout.addWidget(self._build_progress_section())

        # Dashboard
        self.dashboard = DashboardWidget()
        root_layout.addWidget(self.dashboard, 1)

        # Footer controls
        root_layout.addWidget(self._build_footer())

    def _build_header(self):
        """Build the top header bar"""
        header = QFrame()
        header.setObjectName("header_frame")
        header.setFixedHeight(70)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(12)

        # Left — title
        title_block = QVBoxLayout()
        title_block.setSpacing(2)

        title = QLabel("WIRE-TEST")
        title.setObjectName("title_label")

        subtitle = QLabel("NETWORK SPEED & STABILITY ANALYZER")
        subtitle.setObjectName("subtitle_label")

        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        # Right — version tag
        version = QLabel("v1.0")
        version.setObjectName("subtitle_label")
        version.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addLayout(title_block)
        layout.addStretch()
        layout.addWidget(version)

        return header

    def _build_progress_section(self):
        """Build the progress bar and status label section"""
        container = QWidget()
        container.setFixedHeight(48)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 6, 24, 6)
        layout.setSpacing(4)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("test_progress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)

        # Status label
        self.status_label = QLabel("Ready — press RUN TEST to begin")
        self.status_label.setObjectName("status_idle")

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)

        return container

    def _build_footer(self):
        """Build the bottom control bar"""
        footer = QFrame()
        footer.setObjectName("header_frame")
        footer.setFixedHeight(64)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(12)

        # Stage indicators
        self.stage_isp      = self._make_stage_dot("ISP")
        self.stage_ping     = self._make_stage_dot("PING")
        self.stage_speed    = self._make_stage_dot("SPEED")
        self.stage_stability = self._make_stage_dot("STABILITY")

        for widget in [
            self.stage_isp,
            self.stage_ping,
            self.stage_speed,
            self.stage_stability
        ]:
            layout.addWidget(widget)

        layout.addStretch()

        # Stop button
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setObjectName("stop_button")
        self.stop_btn.setFixedWidth(100)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)

        # Run button
        self.run_btn = QPushButton("RUN TEST")
        self.run_btn.setFixedWidth(140)
        self.run_btn.clicked.connect(self._on_run)

        layout.addWidget(self.stop_btn)
        layout.addWidget(self.run_btn)

        return footer

    def _make_stage_dot(self, label):
        """Create a stage indicator with dot + label"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        dot = QLabel("●")
        dot.setObjectName("status_idle")
        dot.setFixedWidth(14)

        text = QLabel(label)
        text.setObjectName("metric_key")

        layout.addWidget(dot)
        layout.addWidget(text)

        # Store dot reference for updates
        widget._dot = dot
        return widget

    def _set_stage(self, stage):
        """Update stage indicator dots"""
        stage_map = {
            "ISP_INFO":   self.stage_isp,
            "PING":       self.stage_ping,
            "SPEED":      self.stage_speed,
            "STABILITY":  self.stage_stability,
        }

        # Reset all to idle
        for widget in stage_map.values():
            widget._dot.setObjectName("status_idle")
            widget._dot.style().unpolish(widget._dot)
            widget._dot.style().polish(widget._dot)

        # Set current to running
        if stage in stage_map:
            stage_map[stage]._dot.setObjectName("status_running")
            stage_map[stage]._dot.style().unpolish(stage_map[stage]._dot)
            stage_map[stage]._dot.style().polish(stage_map[stage]._dot)

        # Set done stages to green
        stages_order = ["ISP_INFO", "PING", "SPEED", "STABILITY"]
        if stage in stages_order:
            idx = stages_order.index(stage)
            for i in range(idx):
                done_widget = stage_map[stages_order[i]]
                done_widget._dot.setObjectName("status_done")
                done_widget._dot.style().unpolish(done_widget._dot)
                done_widget._dot.style().polish(done_widget._dot)

    def _on_run(self):
        """Start the test worker"""
        # Reset UI
        self.dashboard.reset()
        self.progress_bar.setValue(0)
        self._update_status("Initializing tests...", "status_running")

        # Disable run, enable stop
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # Create and connect worker
        self.worker = TestWorker(stability_duration=30)

        self.worker.progress_updated.connect(self._on_progress)
        self.worker.stage_updated.connect(self._set_stage)
        self.worker.isp_result.connect(self.dashboard.update_isp)
        self.worker.ping_result.connect(self.dashboard.update_ping)
        self.worker.speed_result.connect(self.dashboard.update_speed)
        self.worker.stability_result.connect(self.dashboard.update_stability)
        self.worker.stability_ping.connect(self.dashboard.update_live_ping)
        self.worker.all_done.connect(self._on_done)
        self.worker.error_occurred.connect(self._on_error)

        self.worker.start()

    def _on_stop(self):
        """Stop the running worker"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self._update_status("Test stopped by user.", "status_error")
            self.run_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    def _on_progress(self, percent, message):
        """Update progress bar and status"""
        self.progress_bar.setValue(percent)
        self._update_status(message, "status_running")

    def _on_done(self):
        """Handle test completion"""
        self.progress_bar.setValue(100)
        self._update_status("All tests complete.", "status_done")
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        # Set all stage dots to done
        for widget in [
            self.stage_isp,
            self.stage_ping,
            self.stage_speed,
            self.stage_stability
        ]:
            widget._dot.setObjectName("status_done")
            widget._dot.style().unpolish(widget._dot)
            widget._dot.style().polish(widget._dot)

    def _on_error(self, error_message):
        """Handle worker errors"""
        self._update_status(f"Error: {error_message}", "status_error")
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _update_status(self, message, object_name="status_idle"):
        """Update status label text and style"""
        self.status_label.setText(message)
        self.status_label.setObjectName(object_name)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("wire-test")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()