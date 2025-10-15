# test/test_can/test_can_basic.py

import time
import can

from hardware.can.can_interface_peak import CANInterfacePeak
from hardware.hardware_enums import PCANCh,  Baudrate, CANFDDLC, PendingDuration
import logging
from typing import List

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def make_can_message(arbitration_id:int,
                     data:List[int],
                     exteded:bool=False,
                     min_dlc:int=8) -> can.Message:
    if len(data) < min_dlc:
        data = data + [0x00] * (min_dlc - len(data))
    return can.Message(
                        arbitration_id=arbitration_id,
                        is_extended_id=False,
                        dlc=max(len(data), min_dlc),
                        data=data
                        )

def wakeup_ecu(channel = PCANCh.DEFAULT_PCAN_CH):
    logger.debug("Opening CAN bus for wakeup...")

    bus = can.interface.Bus(
        channel=PCANCh.DEFAULT_PCAN_CH,
        interface="pcan",
        bitrate=500000
    )

    try:
        logger.debug("Starting wakeup sequence...")
        start_time=time.time()
        while time.time() - start_time < 1.5:
            msg = make_can_message(0x638, [0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
            bus.send(msg)

            logger.debug(f"Sent wakeup: ID=0x{msg.arbitration_id:X}, Data={msg.data}")
            time.sleep(PendingDuration.DEFAULT)
        logger.debug("Wakeup sequence complete.")

    except can.CanError as e:
        logger.error(f"CAN error during wakeup: {e}")

    finally:
        bus.shutdown()
        logger.debug("CAN bus closed after wakeup.")

def wakeup_ecu(channel = PCANCh.DEFAULT_PCAN_CH):
    logger.debug("Opening CAN bus for wakeup...")

    bus = can.interface.Bus(
        channel=PCANCh.DEFAULT_PCAN_CH,
        interface="pcan",
        bitrate=500000
    )

    try:
        logger.debug("Starting wakeup sequence...")
        start_time=time.time()
        while time.time() - start_time < 1.5:
            msg = make_can_message(0x638, [0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
            bus.send(msg)

            logger.debug(f"Sent wakeup: ID=0x{msg.arbitration_id:X}, Data={msg.data}")
            time.sleep(PendingDuration.DEFAULT)
        logger.debug("Wakeup sequence complete.")

    except can.CanError as e:
        logger.error(f"CAN error during wakeup: {e}")

    finally:
        bus.shutdown()
        logger.debug("CAN bus closed after wakeup.")


def test_peak_can_dlc(channel: str = PCANCh.DEFAULT_PCAN_CH):
    logger.debug("Entered test_peak_can_dlc()")

    # --- Phase 1: Classic CAN wakeup ---
    bus = CANInterfacePeak(channel=channel)
    wakeup_id = 0x638
    wakeup_data = [0x01]

    try:
        # Open as Classic CAN (no data_bitrate!)
        bus.open(bitrate=Baudrate._500kbps)
        logger.info("Classic CAN bus opened successfully for wakeup")

        i = 0x01
        for _ in range(20):
            bus.send(            # Classic CAN
                arbitration_id=wakeup_id,
                data=wakeup_data,
                fd=False,
                is_extended_id=False
            )
            i += 1
            wakeup_data += [i]
            logger.info(f"wakeup_data = {wakeup_data}")

            logger.info(f"Sent wakeup message: ID=0x{wakeup_id:X}, DATA={wakeup_data}")
            time.sleep(PendingDuration._3ms)

        logger.info("Wakeup completed.")
    finally:
        bus.close()
        logger.info("Closed Classic CAN bus after wakeup")
    #
    # # --- Phase 2: CAN FD diagnostics ---
    # bus = CANInterfacePeak(channel=channel)
    # try:
    #     bus.open(bitrate=Baudrate._500kbps, data_bitrate=Baudrate._2mbps)
    #     logger.info("CAN FD bus opened successfully for diagnostics")
    #
    #     BDF_40 = 0x14DA40F1
    #
    #     # 10 03 Service
    #     BDF_10_03 = [0x02, 0x10, 0x03]
    #     logger.info("Before         bus.send(arbitration_id=BDF_40, data=BDF_10_03, fd=True, is_extended_id=True)")
    #     bus.send(arbitration_id=BDF_40, data=BDF_10_03, fd=True, is_extended_id=True, pad_to_min=CANFDDLC.DLC_8)
    #     logger.info("After         bus.send(arbitration_id=BDF_40, data=BDF_10_03, fd=True, is_extended_id=True)")
    #     time.sleep(PendingDuration._10ms)
    #
    #     # 27 01 Service
    #     BDF_27_01 = [0x02, 0x27, 0x01]
    #     bus.send(arbitration_id=BDF_40, data=BDF_27_01, fd=True, is_extended_id=True, pad_to_min=CANFDDLC.DLC_8)
    #     logger.info("After         bus.send(arbitration_id=BDF_40, data=BDF_27_01, fd=True, is_extended_id=True, pad_to_min=CANFDDLC.DLC_8)")
    #     time.sleep(PendingDuration.DEFAULT)
    #
    #     #
    #     # CANFD mutiple frame
    #     bool_mutiple_frame_2702:bool = True
    #     #
    #
    #     if bool_mutiple_frame_2702:
    #
    #         BDF_27_02_1 = [0X00, 0x0E, 0x27, 0x02, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x11, 0x12]
    #         bus.send(arbitration_id=BDF_40, data=BDF_27_02_1, fd=True, is_extended_id=True, pad_to_min=CANFDDLC.DLC_16)
    #         logger.info("After [0X00, 0x0E, 0x27, 0x02, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x11, 0x12]")
    #         time.sleep(PendingDuration._30ms)
    #     else:
    #         # 27 02 Service
    #         BDF_27_02_1 = [0X10, 0x0E, 0x27, 0x02, 0x01, 0x02, 0x03, 0x04]
    #         bus.send(arbitration_id=BDF_40, data=BDF_27_02_1, fd=True, is_extended_id=True, pad_to_min=CANFDDLC.DLC_8)
    #         logger.info("After [0x0E, 0x27, 0x02, 0x01, 0x02, 0x03, 0x04]")
    #         time.sleep(PendingDuration.DEFAULT)
    #
    #         BDF_27_02_2 = [0x21, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x11]
    #         bus.send(arbitration_id=BDF_40, data=BDF_27_02_2, fd=True, is_extended_id=True, pad_to_min=CANFDDLC.DLC_8)
    #         logger.info("After [0x21, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x11]")
    #         time.sleep(PendingDuration.DEFAULT)
    #
    #         BDF_27_02_3 = [0x22, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    #         bus.send(arbitration_id=BDF_40, data=BDF_27_02_3, fd=True, is_extended_id=True, pad_to_min=CANFDDLC.DLC_8)
    #         logger.info("After [0x22, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]")
    #         time.sleep(PendingDuration.DEFAULT)
    #
    #
    #     BDF_2F_PM = [0X07, 0x2F, 0xFD, 0x04, 0x03, 0x80, 0x00, 0x03]
    #     bus.send(arbitration_id=BDF_40, data=BDF_2F_PM, fd=True, is_extended_id=True, pad_to_min=CANFDDLC.DLC_8)
    #     logger.info(
    #         "After [0X07, 0x2F, 0xFD, 0x04, 0x03, 0x80, 0x00, 0x03]")
    #     time.sleep(PendingDuration.DEFAULT)
    #
    #
    #     logger.info("Diagnostic sequence complete.")
    # finally:
    #     bus.close()
    #     logger.info("Closed CAN FD bus after diagnostics")


        # BDF_40 = 0x14DA40F1
        # BDF_27_02_1 = [0x10, 0x0E, 0x27, 0x02, 0x01, 0x02, 0x03, 0x04]
        # bus.send(arbitration_id=BDF_40, data=BDF_27_02_1, fd=True, is_extended_id=True, pad_to_min=8)
        # time.sleep(0.05)

        # BDF_40 = 0x14DA40F1
        # BDF_27_02_2 = [0x21, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x11]
        # bus.send(arbitration_id=BDF_40, data=BDF_27_02_2, fd=True, is_extended_id=True, pad_to_min=8)
        # time.sleep(0.05)
        #
        # BDF_40 = 0x14DA40F1
        # BDF_27_02_3 = [0x22, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        # bus.send(arbitration_id=BDF_40, data=BDF_27_02_3, fd=True, is_extended_id=True, pad_to_min=8)
        # time.sleep(0.05)

"""


"""

