# /business/workers/can_validation_thread.py

import threading
import queue
from business.can_decoder import CANDecoder
from business.can_validator import Validator
from hardware.can.PCANBasic import TPCANMsgFD
# Assuming this lookup table is correctly imported from your can_fd library:
from can_fd.canfd.canfd_enum import DLC_2_LEN
from hardware.can.pcan_constants import *
from business.workers.can_state_store import CanStateStore  # CRITICAL IMPORT


class ValidationThread(threading.Thread):
    def __init__(self, frame_queue: queue.Queue, decoder_cfg: str, validation_cfg: str, stop_event,
                 can_state_store: CanStateStore):
        super().__init__()
        self.frame_queue = frame_queue
        # Initialize the decoding and validation classes
        self.decoder = CANDecoder(decoder_cfg)
        self.validator = Validator(validation_cfg)
        self.stop_event = stop_event
        # Store the shared state object
        self.can_state_store = can_state_store

    def run(self):
        while not self.stop_event.is_set():
            try:
                # Attempt to get a message from the queue with a timeout to check stop_event
                msg = self.frame_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            # safety check remains
            if not isinstance(msg, TPCANMsgFD):
                continue

            # 1. Extract ID
            can_id = msg.ID

            # 2. Determine Payload Length
            if msg.MSGTYPE & PCAN_MESSAGE_FD:
                # CAN FD: use lookup table to find actual data length from DLC
                payload_length = DLC_2_LEN.get(msg.DLC, 0)
            else:
                # Classical CAN: DLC is the length (0-8)
                payload_length = msg.DLC

            # 3. Slice the data to the actual payload length and convert to bytes
            data = bytes(msg.DATA[:payload_length])

            # 4. Decode Signals
            decoded = self.decoder.decode(can_id, data)

            # 5. Process Decoded Signals (CRITICAL CHANGE)
            for sig, val in decoded.items():

                if sig in ["Vehicle_Power_Mode", "Windshield_Wiper_Switch_Status"]:
                    print(f"   [ValidationThread] Decoded: {sig} = {val}")

                # Feed the validator for history and final result checks
                self.validator.feed(sig, val)

                # Feed the shared state store for real-time monitoring and UI updates
                self.can_state_store.update_state(sig, val)

    def get_results(self):
        """Returns the final validation results aggregated over the test run."""
        return self.validator.validate_all()