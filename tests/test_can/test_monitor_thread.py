# tests/test_can/test_monitor_thread.py

import threading
import time
import logging
from typing import List
from queue import Queue

from hardware.can.PCANBasic import *


from hardware.can.pcan_constants import (
    PCAN_MESSAGE_STANDARD,
    PCAN_MESSAGE_EXTENDED,
    PCAN_MESSAGE_RTR,
    PCAN_MESSAGE_FD,
    PCAN_MESSAGE_BRS,
    bitrate_fd_500K_2Mb,
)


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global queue to hand off RX messages to main
rx_queue = Queue()


# --- Formatter helpers ---
def fmt_id(can_id: int, extended: bool) -> str:
    """Format CAN ID with h suffix (like 15Eh)."""
    return f"0x{can_id:08X}" if extended else f"{can_id:03X}h"


def fmt_data(data: List[int]) -> str:
    """Format data bytes like [8Dh, 58h, 47h]."""
    return "[" + ", ".join(f"{b:02X}" for b in data) + "]"


def wakeup_thread(pcan: PCANBasic, channel, stop_event: threading.Event, interval: float = 0.05):
    """
    Continuously send CAN wakeup message (ID=0x638, 8 bytes).
    Runs until stop_event is set.

    Args:
        pcan: PCANBasic instance
        channel: PCAN channel (e.g., PCAN_USBBUS1)
        stop_event: threading.Event to stop the thread
        interval: interval between messages in seconds (default 100 ms)
    """
    logger.info("Wakeup thread started")

    msg = TPCANMsgFD()
    msg.ID = 0x638
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD      # Classical CAN frame
    msg.DLC = 8
    msg.DATA[0:8] = (0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)

    while not stop_event.is_set():
        result = pcan.WriteFD(channel, msg)

        if result == PCAN_ERROR_OK:
            logger.debug(
                f"WAKEUP TX: ID={fmt_id(msg.ID, False)}, DLC={msg.DLC}; Data={fmt_data([msg.DATA[i] for i in range(msg.DLC)])}"
            )
        else:
            logger.error(f"Wakeup TX failed: {pcan.GetErrorText(result)}")

        time.sleep(interval)

    logger.info("Wakeup thread stopped")



def wakeup_thread_duplicate(pcan: PCANBasic, channel, stop_event: threading.Event, interval: float = 0.05):
    """
    Continuously send CAN wakeup message (ID=0x638, 8 bytes).
    Runs until stop_event is set.

    Args:
        pcan: PCANBasic instance
        channel: PCAN channel (e.g., PCAN_USBBUS1)
        stop_event: threading.Event to stop the thread
        interval: interval between messages in seconds (default 100 ms)
    """
    logger.info("wakeup_thread_duplicate started")

    msg = TPCANMsgFD()
    msg.ID = 0x14DA40F1
    msg.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS       # Classical CAN frame
    msg.DLC = 8
    msg.DATA[0:8] = (0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00)

    while not stop_event.is_set():
        result = pcan.WriteFD(channel, msg)

        if result == PCAN_ERROR_OK:
            logger.debug(
                f"WAKEUP TX: ID={fmt_id(msg.ID, False)}, DLC={msg.DLC}; Data={fmt_data([msg.DATA[i] for i in range(msg.DLC)])}"
            )
        else:
            logger.error(f"Wakeup TX failed: {pcan.GetErrorText(result)}")

        time.sleep(interval)

    logger.info("Wakeup thread stopped")







def rx_thread(pcan: PCANBasic, channel, stop_event: threading.Event):
    logger.info("RX thread started")

    while not stop_event.is_set():
        res, rmsg, rtime = pcan.ReadFD(channel)

        if res == PCAN_ERROR_OK:
            is_fd = bool(rmsg.MSGTYPE & PCAN_MESSAGE_FD)
            dlc = rmsg.DLC
            data = [rmsg.DATA[i] for i in range(dlc)]

            frame_info = {
                "id": rmsg.ID,
                "dlc": dlc,
                "data": data,
                "fd": is_fd,
                "brs": bool(rmsg.MSGTYPE & PCAN_MESSAGE_BRS),
            }
            rx_queue.put(frame_info)

        elif res == PCAN_ERROR_QRCVEMPTY:
            time.sleep(0.001)
        else:
            sts = pcan.GetErrorText(res)
            logger.error(f"RX error: {sts}")


def pcan_conflict_try():

    logger.info("pcan_conflict_try() started")

    channel = PCAN_USBBUS1
    pcan = PCANBasic()

    result = pcan.InitializeFD(channel, bitrate_fd_500K_2Mb)
    if result != PCAN_ERROR_OK:
        logger.error(f"PCAN_Monitor_Demo failed: {pcan.GetErrorText(result)}")
        return
    logger.info("PCAN_Monitor_Demo initialized")

    stop_event = threading.Event()

    t_wakeup = None
    t_wakeup_duplicate = None

    interval = 0.0000005

    try:
        t_wakeup = threading.Thread(target=wakeup_thread, args=(pcan, channel, stop_event, interval), daemon=True)
        t_wakeup.start()

        t_wakeup_duplicate = threading.Thread(target=wakeup_thread_duplicate, args=(pcan, channel, stop_event, interval), daemon=True)
        t_wakeup_duplicate.start()
        time.sleep(200)

    finally:
        stop_event.set()
        t_wakeup.join(timeout=1.0)
        t_wakeup_duplicate.join(timeout=1.0)
        pcan.Uninitialize(channel)
        logger.info("PCAN closed")



def monitor_thread_Try():
    channel = PCAN_USBBUS1
    pcan = PCANBasic()

    result = pcan.InitializeFD(channel, bitrate_fd_500K_2Mb)
    if result != PCAN_ERROR_OK:
        logger.error(f"PCAN_Monitor_Demo failed: {pcan.GetErrorText(result)}")
        return
    logger.info("PCAN_Monitor_Demo initialized")

    # Create stop event and start thread
    stop_event = threading.Event()
    t = threading.Thread(target=rx_thread, args=(pcan, channel, stop_event), daemon=True)
    t.start()

    try:
        # --- Sending frames here (same as your code) ---
        msg = TPCANMsgFD()
        msg.ID = 0x638
        msg.MSGTYPE = PCAN_MESSAGE_STANDARD
        msg.DLC = 8
        msg.DATA[0:8] = (0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)

        for _ in range(3):
            result = pcan.WriteFD(channel, msg)
            if result == PCAN_ERROR_OK:
                logger.info(
                    f"TX-CAN: ID={fmt_id(msg.ID, False)}, DLC={msg.DLC}; Data={fmt_data([msg.DATA[i] for i in range(msg.DLC)])}"
                )
            else:
                logger.error(f"SendFD failed: {pcan.GetErrorText(result)}")
            time.sleep(0.05)


        # Extended CAN FD frame
        msg = TPCANMsgFD()
        msg.ID = 0x14DA40F1
        msg.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg.DLC = 8
        msg.DATA[0:8] = (0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00)
        result = pcan.WriteFD(channel, msg)
        if result == PCAN_ERROR_OK:
            logger.info(
                f"TX-FD: ID={fmt_id(msg.ID, True)}, DLC={msg.DLC}; Data={fmt_data([msg.DATA[i] for i in range(msg.DLC)])}"
            )
        else:
            logger.error(f"SendFD failed: {pcan.GetErrorText(result)}")

        # --- Main loop: process received frames ---
        for _ in range(50):
            try:
                frame = rx_queue.get(timeout=0.1)
                if frame["fd"]:
                    logger.info(
                        f"RX-FD: ID={fmt_id(frame['id'], frame['ext'])}, DLC={frame['dlc']}; "
                        f"Data={fmt_data(frame['data'])}, BRS={frame['brs']}, Time={frame['timestamp_us']} µs"
                    )
                else:
                    logger.info(
                        f"RX-CAN: ID={fmt_id(frame['id'], frame['ext'])}, DLC={frame['dlc']}; "
                        f"Data={fmt_data(frame['data'])}, Time={frame['timestamp_us']} µs"
                    )
            except Exception:
                pass
            time.sleep(0.05)

    finally:
        stop_event.set()
        t.join(timeout=1.0)
        pcan.Uninitialize(channel)
        logger.info("PCAN closed")