# tests/test_can/test_vaa_2.py

import threading, time, logging
import queue

from business.can_validation_thread import ValidationThread
from business.uds_services import UDSServices
from hardware.can.PCANBasic import PCANBasic, TPCANMsgFD
from hardware.can.can_logger import setup_can_logger
from hardware.can.can_workers import rx_monitor, periodic_tx
from hardware.can.pcan_constants import *

from business.can_decoder import CANDecoder
from business.can_validator import Validator



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)






def can_comm_test():

    """ PCAN Init """
    channel = PCANCh.default
    pcan = PCANBasic()
    pcan.InitializeFD(channel, bitrate_fd_500K_2Mb)
    pcan.SetValue(channel, PCAN_ALLOW_ECHO_FRAMES, PCAN_PARAMETER_ON)   # Enable echo frames
    time.sleep(0.5)  # Wait pcan init,

    """ thread stop Init """
    stop_event = threading.Event()

    """ can frame list """
    frame_queue = queue.Queue()

    """ RX thread """
    can_logger = setup_can_logger()
    t_rx = threading.Thread(
        target=rx_monitor,args=(pcan, channel, stop_event, can_logger, frame_queue),daemon=True)
    t_rx.start()

    """ CAN State Monitor thread """
    # Start validation worker
    validator_thread = ValidationThread(
        frame_queue,
        decoder_cfg="config/CAN_Decode_PN12345678.yaml",
        validation_cfg="config/CAN_Validation_PN12345678.yaml",
        stop_event=stop_event
    )
    validator_thread.start()



    """ wake up thread """
    msg_wakeup = TPCANMsgFD()
    msg_wakeup.ID = 0x638
    msg_wakeup.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg_wakeup.DLC = 8
    msg_wakeup.DATA[0:8] = (0x08, 0, 0, 0, 0, 0, 0, 0)

    t_wakeup = threading.Thread(target=periodic_tx, args=(pcan, channel, stop_event, msg_wakeup, logger, 0.5), daemon=True)
    t_wakeup.start()


    """ Tester Present thread """
    msg_tester_present = TPCANMsgFD()
    msg_tester_present.ID = 0x14DA40F1
    msg_tester_present.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD
    msg_tester_present.DLC = 8
    msg_tester_present.DATA[0:8] = (0x02, 0x3E, 0x80, 0, 0, 0, 0, 0)

    t_tester_present = threading.Thread(target=periodic_tx, args=(pcan, channel, stop_event, msg_tester_present, logger, 4.5), daemon=True)
    t_tester_present.start()


    """ Perform UDS diagnostic sequence """
    time.sleep(3.0) # wait multiple thread to execute and BDF to wakeup
    uds = UDSServices(pcan, channel)
    uds.diagnostic_session_control(0x03)
    uds.security_access_request_seed(1)
    uds.security_access_send_key(b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C")
    uds.io_control(0xFD04, [0x03, 0x80, 0x00, 0x03])


    sleep_s:int = 600
    time.sleep(sleep_s)




    """"""""""""""""""""""""""""""""" 
    #   Test End 
    """""""""""""""""""""""""""""""""

    # Later, stop & collect results
    stop_event.set()


    validator_thread.join()
    results = validator_thread.get_results()

    logger.info(results)

    """ Close hardware """
    pcan.Uninitialize(channel)
