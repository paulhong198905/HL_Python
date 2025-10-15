# business/workers/can_signal_monitor_worker.py

import queue
import threading  # Use threading.Event to keep signature clean
import logging
from PySide6.QtCore import QThread, Signal
from business.can_decoder import CANDecoder
from hardware.can.PCANBasic import TPCANMsgFD
from can_fd.canfd.canfd_enum import DLC_2_LEN
from hardware.can.pcan_constants import *

logger = logging.getLogger(__name__)


class CanSignalMonitorWorker(QThread):
    # Wiper Signal: Emits decoded string state (e.g., "LOW", "OFF")
    sig_wiper_status_state_changed = Signal(str)

    # Power Model Signal: Emits decoded string state (e.g., "RUN", "OFF")
    sig_power_model_state_changed = Signal(str)

    # Hard-coded details for the demo
    TARGET_WIPER_SIGNAL_NAME = "Windshield_Wiper_Switch_Status"
    TARGET_PM_SIGNAL_NAME = "Power_Model_Status"  # Assuming this is your Power Model Signal

    def __init__(self, frame_queue: queue.Queue, decoder_cfg: str, stop_event: threading.Event, parent=None):
        super().__init__(parent)
        self.frame_queue = frame_queue
        self.stop_event = stop_event

        # Initialize decoder and state trackers
        self.decoder = CANDecoder(decoder_cfg)
        self._last_wiper_state = None
        self._last_pm_state = None

    def run(self):
        logger.info("[CAN MONITOR] Worker started, monitoring Wiper and Power Model status.")

        while not self.stop_event.is_set():
            try:
                msg = self.frame_queue.get(timeout=0.05)
            except queue.Empty:
                continue

            if not isinstance(msg, TPCANMsgFD):
                continue

            can_id = msg.ID

            if msg.MSGTYPE & PCAN_MESSAGE_FD:
                payload_length = DLC_2_LEN.get(msg.DLC, 0)
            else:
                payload_length = msg.DLC

            data = bytes(msg.DATA[:payload_length])

            decoded = self.decoder.decode(can_id, data)

            # --- Wiper Status Tracking ---
            if self.TARGET_WIPER_SIGNAL_NAME in decoded:
                current_state = decoded[self.TARGET_WIPER_SIGNAL_NAME]

                if current_state != self._last_wiper_state:
                    self._last_wiper_state = current_state
                    self.sig_wiper_status_state_changed.emit(current_state)
                    logger.debug(f"[CAN MONITOR] Wiper state changed to: {current_state}")

            # --- Power Model Status Tracking ---
            if self.TARGET_PM_SIGNAL_NAME in decoded:
                current_state = decoded[self.TARGET_PM_SIGNAL_NAME]

                if current_state != self._last_pm_state:
                    self._last_pm_state = current_state
                    self.sig_power_model_state_changed.emit(current_state)
                    logger.debug(f"[CAN MONITOR] PM state changed to: {current_state}")

        logger.info("[CAN MONITOR] Worker terminated.")