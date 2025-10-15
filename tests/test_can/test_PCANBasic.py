# test/test_can/test_PCANBasic.py

import logging
import time
from hardware.can.PCANBasic import *
from hardware.hardware_enums import Baudrate
from hardware.can.pcan_constants import *

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)




def PCANBasic_get_info():
    pcan = PCANBasic()
    channel = PCAN_USBBUS1


    # Try to get API version via GetValue
    try:
        sts, api_version = pcan.GetValue(channel, PCAN_API_VERSION)
        if sts == PCAN_ERROR_OK:
            logger.info(f"PCAN API Version: {api_version}")
        else:
            logger.warning(f"PCAN API Version not available, status=0x{sts:X}")
    except Exception as e:
        logger.error(f"PCAN API Version query failed: {e}")


    # Hardware name
    sts, hw_name = pcan.GetValue(channel, PCAN_HARDWARE_NAME)
    if sts == PCAN_ERROR_OK:
        logger.info(f"PCAN Hardware: {hw_name}")

    # Device ID
    sts, dev_id = pcan.GetValue(channel, PCAN_DEVICE_ID)
    if sts == PCAN_ERROR_OK:
        logger.info(f"PCAN Device ID: {dev_id}")









def PCANBasic_CAN_Test():
    """
    Send classic CAN wakeup messages (0x638, 8 bytes) using PCANBasic.
    """
    logger.info(f"Opening demo_pcan_wakup()")
    channel = PCAN_USBBUS1
    pcan = PCANBasic()

    result = pcan.Initialize(channel, PCAN_BAUD_500K)
    if result != PCAN_ERROR_OK:
        sts = pcan.GetErrorText(result)
        logger.error(f"PCAN Initialize failed: {sts}")
        return
    logger.info("PCAN initialized successfully")

    try:
        msg = TPCANMsg()
        msg.ID = 0x638
        msg.LEN = 8
        msg.MSGTYPE = PCAN_MESSAGE_STANDARD  # Classic CAN 11-bit
        msg.DATA = (0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)

        for i in range(3):
            result = pcan.Write(channel, msg)
            if result != PCAN_ERROR_OK:
                sts = pcan.GetErrorText(result)
                logger.error(f"Send failed: {sts}")
            else:
                logger.info(
                    f"Sent wakeup {i+1}: ID=0x{msg.ID:X}, DATA={list(msg.DATA)[:msg.LEN]}"
                )
            time.sleep(0.05)

        # --- Read loop: poll the rx queue ---
        logger.info("Start reading messages from the CAN bus...")

        for _ in range(10):
            res, rmsg, rtime = pcan.Read(channel)
            if res== PCAN_ERROR_OK:
                data_list = [rmsg.DATA[i] for i in range(rmsg.LEN)]
                logger.info(
                    f"RX: ID=0x{rmsg.ID:X}, LEN={rmsg.LEN}, DATA={data_list}, Time={rtime.micros + (rtime.millis*1000)} µs"
                )

            elif res == PCAN_ERROR_QRCVEMPTY:
                # No message in receive queue
                logger.debug("RX queue empty")
            else:
                sts = pcan.GetErrorText(res)
                logger.error(f"Read failed: {sts}")

        time.sleep(0.1)  # small delay between polls

    finally:
        # Always uninitialize
        pcan.Uninitialize(channel)
        logger.info("PCAN closed")


def PCANBasic_CANFD_Test():
    """
    Send one CAN-FD frame with Extended ID 0x14DA40F1
    Data = [0x02, 0x10, 0x03]
    """
    logger.info("Opening PCAN FD test")

    channel = PCAN_USBBUS1
    pcan = PCANBasic()

    # Initialize CAN FD
    result = pcan.InitializeFD(channel, bitrate_fd_500K_2Mb)
    if result != PCAN_ERROR_OK:
        sts = pcan.GetErrorText(result)
        logger.error(f"PCAN InitializeFD failed: {sts}")
        return
    logger.info("PCAN FD initialized successfully")

    try:
        # Build a TPCANMsgFD (CAN FD frame)
        msg = TPCANMsgFD()
        msg.ID = 0x14DA40F1  # 29-bit extended ID
        msg.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg.DLC = 3  # 3 data bytes
        msg.DATA[0] = 0x02
        msg.DATA[1] = 0x10
        msg.DATA[2] = 0x03

        # Send once
        result = pcan.WriteFD(channel, msg)
        if result != PCAN_ERROR_OK:
            sts = pcan.GetErrorText(result)
            logger.error(f"SendFD failed: {sts}")
        else:
            logger.info(
                f"Sent FD frame: ID=0x{msg.ID:X}, MSGTYPE = {msg.MSGTYPE},DLC={msg.DLC}, DATA={[msg.DATA[i] for i in range(msg.DLC)]}"
            )

        time.sleep(0.05)

        # --- Read loop: poll the rx queue ---
        logger.info("Start reading messages from the CAN bus...")

        for i in range(10):
            res, rmsg, rtime = pcan.ReadFD(channel)

            if res == PCAN_ERROR_OK:
                # For CAN FD, use DLC instead of LEN
                dlc = rmsg.DLC
                data_list = [rmsg.DATA[j] for j in range(dlc)]

                logger.info(
                    f"[{i + 1}] RX: ID=0x{rmsg.ID:X}, MessageType = {rmsg.MSGTYPE},DLC={dlc}, DATA={data_list}"
                )


            elif res == 0x00000002:  # PCAN_ERROR_QRCVEMPTY
                # Queue empty, nothing received
                logger.debug(f"[{i+1}] RX queue empty")
            else:
                # Some other error
                sts = pcan.GetErrorText(res)
                logger.error(f"[{i+1}] Read failed: {sts}")

        time.sleep(0.1)  # small delay between polls

    finally:
        # Always uninitialize
        pcan.Uninitialize(channel)
        logger.info("PCAN closed")