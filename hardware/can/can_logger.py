# hardware/can/can_logger.py

import logging
import os
from datetime import datetime
# from typing import List
from hardware.can.PCANBasic import TPCANMsgFD
from hardware.can.pcan_constants import *
from can_fd.canfd.canfd_enum import DLC_2_LEN

# Constants for formatting
ID_FIELD_WIDTH = 12
DATA_FIELD_WIDTH = 44
TYPE_WIDTH = 12
DLC_WIDTH = 5

def setup_can_logger(log_dir: str = "logs") -> logging.Logger:
    """Setup CAN trace logger with timestamped file."""
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Can_Trace_{timestamp}.txt"
    log_path = os.path.join(log_dir, filename)

    can_logger = logging.getLogger(__name__)
    can_logger.setLevel(logging.DEBUG)
    can_logger.handlers.clear()

    # --- New: microsecond formatter ---
    class MicrosecondFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            ct = datetime.fromtimestamp(record.created)
            if datefmt:
                s = ct.strftime(datefmt)
            else:
                s = ct.strftime("%Y-%m-%d %H:%M:%S.%f")
            return s

    fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    fmt = MicrosecondFormatter("%(asctime)s  %(message)s",
                               datefmt="%Y-%m-%d %H:%M:%S.%f")
    fh.setFormatter(fmt)
    can_logger.addHandler(fh)

    # Header
    can_logger.info("===== PCAN Bus Trace Log =====")
    can_logger.info("This log contains all CAN/CAN-FD messages on the bus.")
    can_logger.info("TX = transmitted (echo), RX = received")
    can_logger.info("DLC = DLC on physical bus, not length for the data")
    can_logger.info("----------------------------------------")
    can_logger.info("Dir Type         CAN_ID       DLC & Len   Data")
    can_logger.info("----------------------------------------")

    return can_logger





def fmt_can_id(msg: TPCANMsgFD) -> str:
    is_ext = bool(msg.MSGTYPE & PCAN_MESSAGE_EXTENDED)
    return f"0x{msg.ID:08X}" if is_ext else f"0x{msg.ID:03X}"


def fmt_can_type(msg: TPCANMsgFD) -> str:
    """Return a readable CAN frame type string."""
    if msg.MSGTYPE & PCAN_MESSAGE_ERRFRAME:
        base = "ERRFRAME"
    elif msg.MSGTYPE & PCAN_MESSAGE_STATUS:
        base = "STATUS"
    elif msg.MSGTYPE & PCAN_MESSAGE_FD:
        base = "FD"
    else:
        base = "CAN"

    flags = []
    if msg.MSGTYPE & PCAN_MESSAGE_BRS:
        flags.append("BRS")
    if msg.MSGTYPE & PCAN_MESSAGE_ESI:
        flags.append("ESI")

    return "+".join([base] + flags)


def log_can_message(msg: TPCANMsgFD, logger: logging.Logger):
    """Log a formatted CAN frame."""
    direction = "TX" if (msg.MSGTYPE & PCAN_MESSAGE_ECHO) else "RX"
    dlc_str = f"DLC_x{msg.DLC:X}".ljust(DLC_WIDTH)
    length = DLC_2_LEN.get(msg.DLC, msg.DLC)
    data = " ".join(f"{msg.DATA[i]:02X}" for i in range(length))
    line = f"{direction:<3} {fmt_can_type(msg):<{TYPE_WIDTH}} {fmt_can_id(msg):<{ID_FIELD_WIDTH}} {dlc_str} L{length:<2}  Hex: {data}"
    logger.debug(line)
