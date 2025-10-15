# tests/test_pyside/model.py

import time
import random
from PySide6.QtCore import QThread, Signal

class DataModel(QThread):
    """
    The Data Model/Engine: Simulates continuous CAN traffic and signal changes.
    Inherits QThread to run in its own thread.
    """
    # Define a custom Signal that carries a dictionary of the current status

    status_update = Signal(dict)

    def __init__(self):
        super().__init__()
        self._is_running = True

        self.current_data = {
            "WiperStatus": "OFF",
            "EngineRPM": 0,
            "BatteryVoltage": 12.0,
        }

    def run(self):
        """Main loop from the thread."""
        rpm_states = [0, 800, 1500, 2500]
        wiper_states = ["OFF", "LOW", "HIGH", "INTERMITTENT"]

        while self._is_running:
            # 1. Update internal state (Simulates Validator.feed())
            self.current_data["WiperStatus"] = random.choice(wiper_states)
            self.current_data["EngineRPM"] = random.choice(rpm_states)
            self.current_data["BatteryVoltage"] = round(random.uniform(11.5, 14.0), 1)

            # 2. Emit the signal (Sends data safely to the Controller/View)
            self.status_update.emit(self.current_data.copy())

            time.sleep(0.5)

    def stop(self):
        """Gracefully stop the thread."""
        self._is_running = False
        self.wait()