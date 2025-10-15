# main.py

import datetime
import logging
import time

import os
import can
import isotp
import udsoncan.configs
from can.bit_timing import BitTimingFd
from udsoncan.client import Client
from udsoncan.connections import PythonIsoTpConnection
# HL common imports
from common.logging_HL import setup_logging
# Proj specific imports


from tests.test_can.test_PCANBasic import *

from tests.test_can.test_vaa_2 import can_comm_test

# ==========================
# Global Variable
# ==========================



# ==========================
# Logger Start
# ==========================
logger = logging.getLogger(__name__)  # Declare at module level


# ==========================
# Logger Setup
# ==========================
def log_setup(level=logging.DEBUG, to_console=True, to_file=True):
    """Setup logger for the application with timestamped file in logs folder."""

    # Ensure logs folder exists
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Generate timestamped log filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_dir, f"Log_{timestamp}.txt")

    # Call your existing logging setup
    setup_logging(log_file=log_file, level=level, to_console=to_console, to_file=to_file)

    # Create logger object
    logger = logging.getLogger()

    # Map level number to readable name (DEBUG, INFO, WARNING, etc.)
    level_name = logging.getLevelName(level)
    logger.info(f"Logger started in {level_name} mode. Log file: {log_file}")

    # # Silence or reduce verbosity of python-can loggers
    # logging.getLogger("can").setLevel(logging.INFO)  # or WARNING
    # logging.getLogger("can.pcan").setLevel(logging.INFO)  # or WARNING

    return logger


# ==========================
# Constants
# ==========================

# Constants -- io card
deviceDescription = "PCI-1750,BID#0"



def PCAN_UDS_test_WKM():
    logger.debug("PCAN_UDS_test_WKM() started.")

    bus = PcanBus(channel='PCAN_USBBUS1', bitrate=500000)
    wakeupdata = [0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    wakeupmsg = can.Message(is_extended_id=False, arbitration_id=0x638, data=wakeupdata)

    try:
        bus.send(wakeupmsg)  # wake up CAN
        time.sleep(0.05)
        bus.send(wakeupmsg)  # wake up CAN
        time.sleep(0.05)
        bus.send(wakeupmsg)  # wake up CAN
        time.sleep(0.05)

    except can.CanError as e:
        logger.error(f"Failed to send CAN message: {e}")
    finally:
        bus.shutdown()
        logger.debug("bus bus shutdown complete")

    timingFD = BitTimingFd(f_clock=80000000, nom_brp=10, nom_tseg1=12, nom_tseg2=3, nom_sjw=1, data_brp=4,
                           data_tseg1=7, data_tseg2=2, data_sjw=1)
    bus = PcanBus(channel='PCAN_USBBUS1', bitrate=500000, timing=timingFD)

    txid = 0x14DA28F1
    rxid = 0x14DAF128

    tp_addr = isotp.Address(isotp.AddressingMode.Normal_29bits, txid=txid, rxid=rxid)
    isotp_params = {
        'stmin': 0,
        # 7/2从0修改为32  # Will request the sender to wait 32ms between consecutive frame. 0-127ms or 100-900ns with values from 0xF1-0xF9
        'blocksize': 0,
        # Request the sender to send 8 consecutives frames before sending a new flow control message.# 流控帧单包大小,0为不限制
        'wftmax': 0,  # Number of wait frame allowed before triggering an error
        'tx_data_length': 8,  # Link layer (CAN layer) works with 8 byte payload (CAN 2.0)
        'tx_data_min_length': None,
        # Minimum length of CAN messages. When different from None, messages are padded to meet this length. Works with CAN 2.0 and CAN FD.
        'tx_padding': 0,  # Will pad all transmitted CAN messages with byte 0x00.
        'rx_flowcontrol_timeout': 1000,
        # Triggers a timeout if a flow control is awaited for more than 1000 milliseconds
        'rx_consecutive_frame_timeout': 1000,
        # Triggers a timeout if a consecutive frame is awaited for more than 1000 milliseconds
        # 'squash_stmin_requirement': False,   # When sending, respect the stmin requirement of the receiver. If set to True, go as fast as possible.
        'max_frame_size': 4095,  # Limit the size of receive frame.
        'can_fd': True,
        # 'bitrate_switch':True
    }
    stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)
    conn = PythonIsoTpConnection(stack)
    config = dict(udsoncan.configs.default_client_config)
    config['p2_timeout'] = 5
    config['standard_version'] = 2006  # 2006之后的版本，发送10诊断服务后，会更改P2-timeout时间
    config['data_identifiers'] = {
        0xF190: udsoncan.AsciiCodec(17),  # Codec that read ASCII string. We must tell the length of the string
    }

    with Client(conn, request_timeout=2, config=config) as client:
        try:

            response = client.change_session(0x03)
        except can.CanError as e:
            logger.error(f"Failed to send CAN message: {e}")
        finally:
            bus.shutdown()
            logger.debug("bus bus shutdown complete")


#
# def PCAN_CAN_test():
#     logger.debug("PCAN_CAN_test() started.")
#
#     # Initialize PCAN Bus
#     bus = can.interface.Bus(
#         channel=channel_Peak,
#         interface='pcan',
#         bitrate=500000
#     )
#
#     # CAN message details
#     can_id = 0x621
#     data_bytes = [0xFF] * 8  # 8 bytes, all 0xFF
#
#     msg = can.Message(
#         arbitration_id=can_id,
#         data=data_bytes,
#         is_extended_id=False
#     )
#
#     try:
#         # Send the message multiple times
#         for _ in range(4):
#             bus.send(msg)
#
#         logger.info(f"Sent CAN message ID={hex(can_id)} Data={data_bytes}")
#     except can.CanError as e:
#
#         logger.error(f"Failed to send CAN message: {e}")
#     finally:
#         bus.shutdown()
#         logger.debug("PCAN bus shutdown complete")


# ==========================
# Main
# ==========================
def main():
    # Initialize logger: choose console/file as needed
    logLvl = logging.INFO   # DEBUG, INFO, WARN, ERROR, FATAL, CRITICAL


    logger = log_setup(level=logLvl, to_console=True, to_file=True)

    try:
        logger.debug("main() started.")
        # IOTestManual()
        # PCAN_CAN_test()
        # PCAN_CANFD_test()
        # PCAN_UDS_test()
        # PCAN_UDS_test_WKM()
        # io_test_auto()
        # test_basic_can_send()
        # wakeup_ecu()
        # test_peak_can_dlc()
        # demo_pcan_wakup()

        # PCANBasic_get_info()
        # PCANBasic_CAN_Test()
        # PCANBasic_CANFD_Test()

        can_comm_test()



    except Exception:
        logger.exception("UNEXPECTED ERROR in main.")
    finally:
        logger.info("Press Enter to exit...")
        try:
            # input()
            pass
        except KeyboardInterrupt:
            logger.info("Program interrupted by user (Ctrl+C).")


if __name__ == "__main__":
    main()
