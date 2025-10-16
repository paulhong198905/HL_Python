# business/workers/can_test_worker.py (Updated for CkptModel ownership)

import threading, time, logging
import queue
from typing import Dict, Any

from PySide6.QtCore import QThread, Signal
from hardware.can.PCANBasic import PCANBasic
from hardware.can.pcan_constants import PCANCh
from hardware.can.can_logger import setup_can_logger
from hardware.can.can_workers import rx_monitor
from business.can_validation_thread import ValidationThread
from business.workers.can_state_store import CanStateStore

logger = logging.getLogger(__name__)


class CanTestWorker(QThread):
    """
    QThread managing continuous background monitoring (logging, decoding, and state storage).
    It operates on an already initialized PCANBasic object provided by the CkptModel.
    """

    sig_progress_updated = Signal(str, int)
    sig_test_finished = Signal(bool, str)

    def __init__(self, pcan_instance: PCANBasic, can_state_store: CanStateStore, decoder_cfg: str,
                 validation_cfg: str, parent=None):
        super().__init__(parent)

        # Receives the initialized PCAN object from the CkptModel
        self.pcan = pcan_instance
        self.can_state_store = can_state_store
        self.decoder_cfg = decoder_cfg
        self.validation_cfg = validation_cfg

        # Internal control objects
        self.channel = PCANCh.default
        self.stop_event = threading.Event()
        self.frame_queue = queue.Queue()

        self.t_rx = None
        self.validator_thread = None

    def run(self):
        # --- REMOVED: PCAN Initialization Logic ---
        # The CkptModel must now handle the initialization and error checking before starting this worker.
        self.sig_progress_updated.emit("CAN Hardware Initialized. Starting Threads...", 15)

        # 1. Start RX Monitor Thread (Logging to file and queuing messages)
        logger.info("Starting RX Monitor Thread (Logging Bus Traffic)...")
        can_logger = setup_can_logger()
        self.t_rx = threading.Thread(
            target=rx_monitor,
            # We assume the PCAN object is ready to read from
            args=(self.pcan, self.channel, self.stop_event, can_logger, self.frame_queue),
            daemon=True
        )
        self.t_rx.start()

        # 2. Start CAN State Monitor/Validation Thread (Decoding and state storage)
        logger.info("Starting Validation/Decoding Thread...")
        self.validator_thread = ValidationThread(
            frame_queue=self.frame_queue,
            decoder_cfg=self.decoder_cfg,
            validation_cfg=self.validation_cfg,
            stop_event=self.stop_event,
            can_state_store=self.can_state_store
        )
        self.validator_thread.start()

        self.sig_progress_updated.emit("CAN Bus Monitoring and Decoding Active.", 20)

        # Main loop for QThread until stopped
        while not self.stop_event.is_set():
            self.msleep(100)

        # Cleanup worker threads only
        self._cleanup()

    def _cleanup(self):
        """Stops all internal threads. DOES NOT uninitialize PCANBasic."""
        logger.info("CAN Worker cleanup initiated. Stopping internal threads.")
        self.stop_event.set()

        if self.t_rx and self.t_rx.is_alive():
            self.t_rx.join(1)

        if self.validator_thread and self.validator_thread.is_alive():
            self.validator_thread.join(1)

        # --- REMOVED: PCAN Uninitialization Logic ---
        # self.pcan.Uninitialize(self.channel)
        # The CkptModel (the owner) is now responsible for this cleanup.
        logger.info("CAN Worker internal threads finished.")

    def stop_worker(self):
        self._cleanup()