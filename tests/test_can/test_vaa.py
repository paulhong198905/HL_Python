# tests/test_can/test_vaa.py

import threading
import time
import logging
import os
from datetime import datetime

from hardware.can.PCANBasic import *
from can_fd.canfd.canfd_enum import CANDLC, DLC_2_LEN
from hardware.can.pcan_constants import *


# --- Formatter / RX monitor constants ---
ID_FIELD_WIDTH = 12     # Width reserved for the hex ID (including '0x')
DATA_FIELD_WIDTH = 44   # Width reserved for the data column
DIR_WIDTH      = 4    # 'RX'/'TX'
ID_WIDTH       = 12   # Changed from 10 to 12 to match '0x14DA40F1'
DLC_WIDTH      = 5    # 'DLC_11'
LEN_WIDTH      = 2    # NEW: For 'Len_8' column
DATA_WIDTH     = 48   # Data column width
TYPE_WIDTH     = 12   # Type/flags



# General logger (console + file)
logging.basicConfig(level=logging.info)
logger = logging.getLogger(__name__)


def log_can_header(logger: logging.Logger):
    """Print fixed-width header for CAN trace log."""
    # Updated widths to match your actual log format
    LEN_WIDTH = 6  # Add this constant for the Len column

    # Calculate total width
    total_width = DIR_WIDTH + TYPE_WIDTH + ID_WIDTH + DLC_WIDTH + LEN_WIDTH + DATA_WIDTH + 10

    sep = "-" * total_width
    logger.info(sep)

    # Header that exactly matches your log format
    header = (
        f"{'Dir'.ljust(DIR_WIDTH)}"  # 4 chars
        f"{'Type/Flags'.ljust(TYPE_WIDTH)}"  # 20 chars  
        f"{'CAN_ID'.ljust(ID_WIDTH)}"  # 12 chars
        f"{'DLC'.ljust(DLC_WIDTH)}"  # 6 chars
        f"{'Len'.ljust(LEN_WIDTH)}"  # 6 chars (new column)
        f"{'Data'.ljust(DATA_WIDTH)}"  # 48 chars
    )
    logger.info(header)
    logger.info(sep)



def setup_can_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Setup a dedicated CAN logger with timestamped filename and aligned headers.
    Log filename format: Can_Trace_YYYY-MM-DD_HH-MM-SS.txt
    """
    os.makedirs(log_dir, exist_ok=True)

    # Generate timestamped filename
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Can_Trace_{timestamp_str}.txt"
    log_path = os.path.join(log_dir, filename)

    can_logger = logging.getLogger("CAN_Trace")
    can_logger.setLevel(logging.DEBUG)

    # Remove old handlers to avoid duplicate logs
    if can_logger.hasHandlers():
        can_logger.handlers.clear()

    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s.%(msecs)03d  %(message)s",
                                  datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    can_logger.addHandler(file_handler)

    # Build aligned column titles
    col_title = (
        f"{'Dir':<8}  "
        f"{'Type/Flags '}"
        f"{'CAN_ID':<{ID_FIELD_WIDTH}}  "
        f"{'DLC':<{DLC_WIDTH}}  "  # 'DLC' received on bus
        f"{'Len':<{DLC_WIDTH}}  "  # 'Length' calculated base on 'DLC' 
        f"{'Data':<{DATA_FIELD_WIDTH}}  "
    )

    # Write header info to file directly
    header_lines = [
        "===== PCAN Bus Trace Log =====",
        "This log contains all CAN/CAN-FD messages on the bus.",
        "TX = transmitted (echo), RX = received",
        "DLC = DLC on physical bus, not length for the data",
        "----------------------------------------",
        col_title,
        "----------------------------------------"
    ]
    for line in header_lines:
        can_logger.debug(line)

    return can_logger


# Dedicated CAN trace logger
can_logger = setup_can_logger()




from typing import List

def fmt_can_id(msg: TPCANMsgFD) -> str:
    """
    Format CAN ID string, automatically detecting extended ID.
    Pads left to ID_FIELD_WIDTH.
    Works with normalized int MSGTYPE.
    """
    is_ext = bool(msg.MSGTYPE & PCAN_MESSAGE_EXTENDED)
    id_str = f"0x{msg.ID:08X}" if is_ext else f"0x{msg.ID:03X}"
    return id_str.rjust(ID_FIELD_WIDTH)

def fmt_can_data(data: List[int]) -> str:
    """
    Format CAN data bytes as hex separated by underscores.
    Pads the string to DATA_FIELD_WIDTH for alignment.
    """
    if not data:
        data_str = "Data: EMPTY"
    else:
        data_str = "Data:" + "x" +" ".join(f"{b:02X}" for b in data)
    return data_str.ljust(DATA_FIELD_WIDTH)  # pad right to align columns


def fmt_can_type(msg: TPCANMsgFD) -> str:
    """
    Return a string describing the CAN message type including all flags.
    Examples: Type_CAN, Type_CANFD+BRS+ESI, Type_CAN+RTR, Type_ERRFRAME
    Works with normalized int MSGTYPE.
    """
    parts = []

    # Base type
    if msg.MSGTYPE & PCAN_MESSAGE_ERRFRAME:
        parts.append("T_ERRFRAME")
    elif msg.MSGTYPE & PCAN_MESSAGE_STATUS:
        parts.append("T_STATUS")
    elif msg.MSGTYPE & PCAN_MESSAGE_FD:
        parts.append("T_FD")
    else:
        parts.append("T_CAN")

    # Additional flags
    if msg.MSGTYPE & PCAN_MESSAGE_BRS:
        parts.append("BRS")
    if msg.MSGTYPE & PCAN_MESSAGE_ESI:
        parts.append("ESI")
    # if msg.MSGTYPE & PCAN_MESSAGE_RTR:
    #     parts.append("RTR")
    # if msg.MSGTYPE & PCAN_MESSAGE_ECHO:
    #     parts.append("ECHO")

    return "+".join(parts)


def log_can_message(msg: TPCANMsgFD, logger: logging.Logger = can_logger):
    """
    Log a CAN/CAN-FD message with aligned formatting.
    Displays DLC as hex code (DLC_0xN) and shows full data based on CAN FD DLC mapping.
    """
    # Detect TX echo vs RX
    direction = "TX" if (msg.MSGTYPE & PCAN_MESSAGE_ECHO) else "RX"

    # Display DLC code in hex
    dlc_str = f"D_x{msg.DLC:X}".ljust(DLC_WIDTH)

    # Display lengh in Dec
    length_str = f"L{DLC_2_LEN[msg.DLC]:d}".ljust(DLC_WIDTH)


    # Map DLC to actual byte length
    try:
        # Map DLC to actual byte length
        if msg.DLC <= 8:
            actual_len = msg.DLC  # standard CAN
        else:
            actual_len = DLC_2_LEN.get(msg.DLC, 0)  # fallback to 0 if unknown


    except ValueError:
        actual_len = min(msg.DLC, len(msg.DATA))  # Fallback: safe slice

    # Build data list safely
    data_list = [msg.DATA[i] for i in range(actual_len)]

    # Format CAN data
    data_str = "Data:" + " ".join(f"{b:02X}" for b in data_list)
    # Dynamically adjust width to fit all possible data
    data_str = data_str.ljust(max(DATA_WIDTH, len(data_str) + 2))

    # Format type/flags
    type_str = fmt_can_type(msg).ljust(TYPE_WIDTH)

    # Build final log line
    log_line = f"{direction.ljust(DIR_WIDTH)} {type_str} {fmt_can_id(msg).rjust(ID_WIDTH)} {dlc_str} {length_str} {data_str} "

    # Log
    logger.debug(log_line)
    return log_line


def rx_monitor_thread(pcan: PCANBasic, channel, stop_event: threading.Event, interval: float = 0.001):
    """
    Continuous RX monitor thread for CAN/CAN FD.
    Drains the receive queue completely each cycle until stop_event is set.

    Args:
        pcan: PCANBasic instance
        channel: PCAN channel (e.g., PCAN_USBBUS1)
        stop_event: threading.Event to stop the thread
        interval: sleep interval between queue polls (seconds)
    """
    logger.info("RX monitor thread started")

    msg = TPCANMsgFD()
    timestamp = TPCANTimestampFD()

    while not stop_event.is_set():
        # Drain the receive queue completely
        while True:

            result, msg, timestamp = pcan.ReadFD(channel)

            if result == PCAN_ERROR_OK:
                log_message = log_can_message(msg, logger)
                can_logger.debug(log_message)  # timestamp is auto-added

            elif result == PCAN_ERROR_QRCVEMPTY:  # Empty queue
                # Queue is empty → break inner loop
                break
            else:
                logger.error(f"RX error: {pcan.GetErrorText(result)}")
                break

        # Small sleep to avoid CPU spin
        time.sleep(interval)

        logger.debug("RX monitor thread stopped")




def periodic_tx_thread(pcan: PCANBasic, channel,
                       stop_event: threading.Event,
                       msg:TPCANMsgFD,
                       interval: float = 0.5):
    """
    Periodically transmit a CAN/CAN FD message until stop_event is set.

    Args:
        pcan: PCANBasic instance
        channel: PCAN channel (e.g., PCAN_USBBUS1)
        stop_event: threading.Event to stop the thread
        msg: TPCANMsgFD message to transmit
        interval: interval between messages in seconds (default 100 ms)
    """
    logger.info( f"Periodic TX thread started for ID=0x{msg.ID:X}, DLC={msg.DLC}, every {interval}s" )

    while not stop_event.is_set():
        result = pcan.WriteFD(channel, msg)

        if result == PCAN_ERROR_OK:
            logger.debug(
                f"TX: ID={fmt_can_id(msg)}, DLC={msg.DLC}; "
                f"{fmt_can_data([msg.DATA[i] for i in range(msg.DLC)])}"
            )
        else:
            logger.error(f"TX failed: {pcan.GetErrorText(result)}")

        time.sleep(interval)

    logger.info("Periodic TX thread stopped")

def can_comm_test():

    logger.info("can_comm_test() started")

    # Predefine threads
    t_wakeup = None
    t_3e = None

    stop_event = threading.Event()

    channel = PCANCh.default

    pcan = PCANBasic()

    result = pcan.InitializeFD(channel, bitrate_fd_500K_2Mb)

    if result == PCAN_ERROR_OK:
        # Try to enable echo frames
        result = pcan.SetValue(channel, PCAN_ALLOW_ECHO_FRAMES, PCAN_PARAMETER_ON)
        if result != PCAN_ERROR_OK:
            err_text = pcan.GetErrorText(result)
            logger.warning(f"Echo frames could not be enabled on channel {channel}: {err_text}")
        else:
            logger.info(f"Echo frames enabled on channel {channel}")
    else:
        err_text = pcan.GetErrorText(result)
        logger.error(f"PCAN_Monitor_Demo failed to initialize channel {channel}: {err_text}")


    logger.info("PCAN_Monitor_Demo initialized")

    try:

        """"""
        """   CAN Bus Monitor """
        """"""
        t_rx = threading.Thread(target=rx_monitor_thread, args=(pcan, channel, stop_event), daemon = True,)

        t_rx.start()


        """"""
        """   Wakeup Thread  (0x638: x08 00*7  standard CAN) """
        """"""

        msg_wakeup = TPCANMsgFD()
        msg_wakeup.ID = 0x638
        msg_wakeup.MSGTYPE = PCAN_MESSAGE_STANDARD
        msg_wakeup.DLC = 8
        msg_wakeup.DATA[0:8] = (0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)

        t_wakeup = threading.Thread(
            target=periodic_tx_thread,
            args=(pcan, channel, stop_event, msg_wakeup, 0.5),
            daemon=True,
        )
        t_wakeup.start()

        time.sleep(1) # wait for ECU to wake up


        """"""
        """   Tester Present  0x3E 80 Thread """
        """"""

        msg_3E00 = TPCANMsgFD()
        msg_3E00.ID = 0x14DA40F1
        msg_3E00.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg_3E00.DLC = 8
        msg_3E00.DATA[0:8] = (0x02, 0x3E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)

        t_3e = threading.Thread(
            target=periodic_tx_thread,
            args=(pcan, channel, stop_event, msg_3E00, 2),
            daemon=True,
        )
        t_3e.start()


        time.sleep(0.1) # wait for ECU to process 3E 80


        #######
        # 0x10 03
        #######

        msg_1003 = TPCANMsgFD()
        msg_1003.ID = 0x14DA40F1
        msg_1003.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg_1003.DLC = CANDLC.DLC_8H_8B
        msg_1003.DATA[0:8] = (0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00)

        result = pcan.WriteFD(channel, msg_1003)

        if result == PCAN_ERROR_OK:
            logger.info(
                f"TX: ID={fmt_can_id(msg_1003)}, DLC={msg_1003.DLC}; {fmt_can_data([msg_1003.DATA[i] for i in range(msg_1003.DLC)])}"
            )
        else:
            logger.error(f"SendFD failed: {pcan.GetErrorText(result)}")

        time.sleep(0.08) # wait for ECU to process 10 03

        #######
        # 0x27 01
        #######
        msg_2701 = TPCANMsgFD()
        msg_2701.ID = 0x14DA40F1
        msg_2701.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg_2701.DLC = CANDLC.DLC_8H_8B
        msg_2701.DATA[0:8] = (0x02, 0x27, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00)

        result = pcan.WriteFD(channel, msg_2701)

        if result == PCAN_ERROR_OK:
            logger.info(
                f"TX: ID={fmt_can_id(msg_2701)}, DLC={msg_2701.DLC}; {fmt_can_data([msg_2701.DATA[i] for i in range(msg_2701.DLC)])}"
            )
        else:
            logger.error(f"SendFD failed: {pcan.GetErrorText(result)}")

        time.sleep(0.015) # wait for ECU to process 27 01

        #######
        # 0x27 02
        #######
        msg_2702 = TPCANMsgFD()
        msg_2702.ID = 0x14DA40F1
        msg_2702.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg_2702.DLC = CANDLC.DLC_AH_16B
        msg_2702.DATA[0:16] = (0x00, 0x0E, 0x27, 0x02, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C)

        result = pcan.WriteFD(channel, msg_2702)

        if result == PCAN_ERROR_OK:
            logger.info(
                f"TX: ID={fmt_can_id(msg_2702)}, DLC={msg_2702.DLC}; {fmt_can_data([msg_2702.DATA[i] for i in range(msg_2702.DLC)])}"
            )
        else:
            logger.error(f"SendFD failed: {pcan.GetErrorText(result)}")

        time.sleep(0.08) # wait for ECU to process 27 02

        #######
        # 0x2F FD 04 03 80 00 03
        #######
        msg_2702 = TPCANMsgFD()
        msg_2702.ID = 0x14DA40F1
        msg_2702.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg_2702.DLC = CANDLC.DLC_8H_8B
        msg_2702.DATA[0:8] = (0x07, 0x2F, 0xFD, 0x04, 0x03, 0x80, 0x00, 0x03)

        result = pcan.WriteFD(channel, msg_2702)

        if result == PCAN_ERROR_OK:
            logger.info(
                f"TX: ID={fmt_can_id(msg_2702)}, DLC={msg_2702.DLC}; {fmt_can_data([msg_2702.DATA[i] for i in range(msg_2702.DLC)])}"
            )
        else:
            logger.error(f"SendFD failed: {pcan.GetErrorText(result)}")

        time.sleep(0.08) # wait for ECU to process 27 02

        #######
        # Sleep, simulate program
        #######
        time.sleep(10)

    finally:

        stop_event.set()
        if t_wakeup is not None:
            t_wakeup.join(timeout=1.0)
        if t_3e is not None:
            t_3e.join(timeout=1.0)
        pcan.Uninitialize(channel)
        logger.info("PCAN closed")

