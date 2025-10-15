# hardware/can/can_workers.py
import time
import threading
import logging
import queue
import yaml
from hardware.can.PCANBasic import PCANBasic, TPCANMsgFD, TPCANTimestampFD
from hardware.can.can_logger import log_can_message
from hardware.can.pcan_constants import *
from typing import Any, Dict, Optional


class SignalDecoder(threading.Thread):
    def __init__(self, config_path: str, frame_queue: queue.Queue,
                 state_store: Dict[str, Any], logger: Optional[logging.Logger] = None):
        super().__init__(daemon=True)
        self.config_path = config_path
        self.frame_queue = frame_queue
        self.state_store = state_store  # shared dict with latest signal states
        self.logger = logger or logging.getLogger(__name__)

        # Load config once at init
        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.signal_defs = self.config.get("signals", [])

    def run(self):
        self.logger.info("SignalDecoder thread started.")
        while True:
            frame = self.frame_queue.get()
            if frame is None:  # poison pill for shutdown
                break
            self.decode_frame(frame)

    def decode_frame(self, frame):
        """Try decoding all signals that match this CAN ID."""
        for sig in self.signal_defs:
            if frame.arbitration_id == sig["can_id"]:
                value = self._decode_signal(frame.data, sig)
                if value is not None:
                    self.state_store[sig["test_name"]] = value
                    self.logger.debug(f"{sig['test_name']} = {value}")

    def _decode_signal(self, data: bytes, sig: Dict) -> Any:
        start_byte = sig["start_byte"]
        start_bit = sig["start_bit"]
        bit_length = sig["bit_length"]
        decode_type = sig["decode_type"]

        # Extract raw integer value
        raw_value = self._extract_bits(data, start_byte, start_bit, bit_length)

        if decode_type == "stateencode":
            return sig["values"].get(raw_value, f"UNKNOWN({raw_value})")

        elif decode_type == "linear":
            a = sig["calculation"].get("a", 1.0)
            b = sig["calculation"].get("b", 0.0)
            return raw_value * a + b

        elif decode_type == "rawbyte":
            expected = sig.get("raw_match")
            if expected and list(data[:len(expected)]) == expected:
                return "MATCH"
            return data.hex().upper()

        else:
            return raw_value  # fallback

    @staticmethod
    def _extract_bits(data: bytes, start_byte: int, start_bit: int, bit_length: int) -> int:
        """Extract bit field from data array."""
        byte_val = data[start_byte]
        mask = (1 << bit_length) - 1
        return (byte_val >> start_bit) & mask




def start_decoder(config_path: str,
                  frame_queue: queue.Queue,
                  validation_mgr,
                  stop_event: threading.Event) -> SignalDecoder:
    decoder = SignalDecoder(
        config_path=config_path,
        frame_queue=frame_queue,
        validation_mgr=validation_mgr,
        stop_event=stop_event
    )
    decoder.start()
    return decoder


def rx_monitor(pcan: PCANBasic, channel,
               stop_event: threading.Event,
               logger: logging.Logger,
               frame_queue: queue.Queue,
               poll_interval: float = 0.001):
    """Continuously poll RX queue and log messages."""
    msg, ts = TPCANMsgFD(), TPCANTimestampFD()
    while not stop_event.is_set():
        while True:
            result, msg, ts = pcan.ReadFD(channel)
            if result == PCAN_ERROR_OK:

                """ write can bus message into the log """
                log_can_message(msg, logger)

                """ write can bus message into the log """
                frame_queue.put(msg)  # enqueue valid message

            elif result == PCAN_ERROR_QRCVEMPTY:
                # no more frames in RX queue
                break
            else:
                # unwrap error text safely
                err_code, err_text = pcan.GetErrorText(result)
                if err_code == PCAN_ERROR_OK:
                    logger.error(f"RX error: {err_text.decode('utf-8', errors='ignore')}")
                else:
                    logger.error(f"RX error: 0x{result:X} (failed to decode error text)")
                break
        time.sleep(poll_interval)


def periodic_tx(pcan: PCANBasic, channel, stop_event: threading.Event,
                msg: TPCANMsgFD, logger: logging.Logger,
                interval: float = 0.5):
    """Periodically transmit a CAN frame."""
    logger.info(f"Starting TX thread: ID=0x{msg.ID:X}, interval={interval}s")
    while not stop_event.is_set():
        result = pcan.WriteFD(channel, msg)
        if result != PCAN_ERROR_OK:
            err_code, err_text = pcan.GetErrorText(result)
            if err_code == PCAN_ERROR_OK:
                logger.error(f"TX error: {err_text.decode('utf-8', errors='ignore')}")
            else:
                logger.error(f"TX error: 0x{result:X} (failed to decode error text)")
        time.sleep(interval)
    logger.info("TX thread stopped")
