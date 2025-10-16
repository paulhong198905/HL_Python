# business/workers/can_state_store.py

import threading
from typing import Dict, Any

from PySide6.QtCore import QObject, Signal


class CanStateStore(QObject):
    """
    Thread-safe storage for the latest decoded CAN signal states.
    Emits signals for critical changes (Power Mode, Wiper Status).
    """

    sig_power_mode_changed = Signal(str)
    # FIX: Replace the generic 'Any' with the base type 'object' for the signal definition.
    sig_signal_updated = Signal(str, object)

    def __init__(self):
        super().__init__()
        self.latest_states: Dict[str, Any] = {}
        self.lock = threading.Lock()

    def update_state(self, signal_name: str, value: Any):
        """Called by the background ValidationThread to update a signal state."""
        with self.lock:
            # Only update and signal if the value has actually changed
            if self.latest_states.get(signal_name) == value:
                return

            self.latest_states[signal_name] = value

        # Emit QSignals in the main thread context
        if signal_name == "Vehicle_Power_Mode":
            self.sig_power_mode_changed.emit(str(value))

        # Emit general update for any signal
        # Note: We emit the actual 'value' which can be str, int, float, etc.
        self.sig_signal_updated.emit(signal_name, value)



    def get_state(self, signal_name: str) -> Any:
        """Called by CkptModel/Controller to check current state."""
        with self.lock:
            return self.latest_states.get(signal_name)