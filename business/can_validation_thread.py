# /business/workers/can_validation_thread.py

import threading
import queue
from business.can_decoder import CANDecoder
from business.can_validator import Validator
from hardware.can.PCANBasic import TPCANMsgFD
from can_fd.canfd.canfd_enum import DLC_2_LEN
from hardware.can.pcan_constants import *


class ValidationThread(threading.Thread):
    def __init__(self, frame_queue: queue.Queue, decoder_cfg: str, validation_cfg: str, stop_event):
        super().__init__()
        self.frame_queue = frame_queue
        self.decoder = CANDecoder(decoder_cfg)
        self.validator = Validator(validation_cfg)
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            try:
                msg = self.frame_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            # safety check remains
            if not isinstance(msg, TPCANMsgFD):
                continue

            # 3. Extract ID and Data using the object's attributes
            can_id = msg.ID

            # Check if the message is CAN FD (DLC > 8 or PCAN_MESSAGE_FD flag set)
            if msg.MSGTYPE & PCAN_MESSAGE_FD:
                # Get the actual payload length using the lookup table
                payload_length = DLC_2_LEN.get(msg.DLC, 0)
            else:
                # For classical CAN (DLC 0-8), DLC is the length
                payload_length = msg.DLC

            # slice it to the actual data length
            # 💡 FIX 1: Convert the sliced data to a 'bytes' object for the decoder.
            data = bytes(msg.DATA[:payload_length])

            # Continue with processing
            decoded = self.decoder.decode(can_id, data)

            # decoded signals are fed to the validator.
            for sig, val in decoded.items():
                self.validator.feed(sig, val)

    def get_results(self):
        return self.validator.validate_all()