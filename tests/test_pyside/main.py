# tests/test_pyside/main.py
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QPushButton, QGroupBox, QHBoxLayout
)
from PySide6.QtCore import Qt
from controller import TestController

class DiagnosticView(QWidget):
    """
    The View: The UI that displays live data.
    """

    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle("Live Test Status (PySide6 MVC)")
        self.controller = controller

        self.setup_ui()

        self.controller.start_test()  # Start the data thread on startup

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # --- A. Control Group ---
        control_group = QGroupBox("Test Controls")
        control_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start/Restart Test")
        self.stop_btn = QPushButton("Stop Test")

        self.start_btn.clicked.connect(self.controller.start_test)
        self.stop_btn.clicked.connect(self.controller.stop_test)

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)


        # --- B. Live Data Display ---
        data_group = QGroupBox("Live Signal Data")
        data_layout = QVBoxLayout()

        self.lbl_rpm = QLabel("Engine RPM: --")
        self.lbl_wiper = QLabel("Wiper Status: --")
        self.lbl_voltage = QLabel("Voltage: --")
        self.lbl_test_status = QLabel("Overall Test: PENDING",
                                      alignment=Qt.AlignmentFlag.AlignCenter)


        data_layout.addWidget(self.lbl_rpm)
        data_layout.addWidget(self.lbl_wiper)
        data_layout.addWidget(self.lbl_voltage)
        data_layout.addWidget(self.lbl_test_status)

        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)

    def update_status(self, data: dict, rpm_status: str):
        """
        SLOT: Called safely from the Controller when new data is available.
        Updates the UI elements.
        """
        # Update labels with raw data
        self.lbl_rpm.setText(f"Engine RPM: {data['EngineRPM']} RPM")
        self.lbl_wiper.setText(f"Wiper Status {data['WiperStatus']}")
        self.lbl_voltage.setText(f"Battery Voltage: {data['BatteryVoltage']} V")

        # Update test status label based on Controller logic
        self.lbl_test_status.setText(f"Overall Test: {rpm_status}")

        # Change color based on status(simple example)
        if "FAIL" in rpm_status:
            self.lbl_test_status.setStyleSheet("Color: red; font-weight: bold,")
        else:
            self.lbl_test_status.setStyleSheet("color: green; font-weight: bold;")

    def closeEvent(self, event):
        """Ensures the background thread stops when the window is closed."""
        self.controller.stop_test()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 1. Instantiate the Controller and pass it the View
    # (The View is not yet created, so we pass the Controller to the View's __init__)

    # 2. Instantiate the View, which receives the Controller
    # The View then calls start_test() on the Controller, launching the thread.

    # Note: We must define the controller variable first to ensure it's not garbage collected
    # before the application runs.

    controller = TestController(None)
    view = DiagnosticView(controller)

    # Now set the view instance on the controller
    controller.view = view

    view.show()
    sys.exit(app.exec())