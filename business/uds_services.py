# business/uds_services.py
import time
import logging
from typing import List

from can_fd.canfd.canfd_enum import CANDLC

from hardware.can.pcan_constants import *
from hardware.can.PCANBasic import TPCANMsgFD


logger = logging.getLogger(__name__)


class UDSServices:
    def __init__(self, pcan, channel):
        self.m_pcan = pcan
        self.m_channel = channel

    def tx(self, msg, wait_s, float = 0.05):
        """Helper to send and log a UDS request."""
        result = self.m_pcan.WriteFD(self.m_channel, msg)

        if result == PCAN_ERROR_OK:
            logger.debug(f"TX: ID={hex(msg.ID)}, DLC={msg.DLC};  {[msg.DATA[i] for i in range(msg.DLC)]}")
        else:
            logger.error(f"SendFD failed: {self.m_pcan.GetErrorText(result)}")

        if wait_s > 0:
            time.sleep(wait_s)

    def diagnostic_session_control(self, subfunction: int = 0x03):
        msg = TPCANMsgFD()
        msg.ID = 0x14DA40F1
        msg.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg.DLC = CANDLC.DLC_8H_8B
        msg.DATA[0:8] = (0x02, 0x10, subfunction, 0, 0, 0, 0, 0)
        self.tx(msg, wait_s=0.8)

    def security_access_request_seed(self, level: int = 1):
        msg = TPCANMsgFD()
        msg.ID = 0x14DA40F1
        msg.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg.DLC = CANDLC.DLC_8H_8B
        msg.DATA[0:8] = (0x02, 0x27, level, 0, 0, 0, 0, 0)
        self.tx(msg, wait_s=0.2)

    def security_access_send_key(self, key: bytes):
        msg = TPCANMsgFD()
        msg.ID = 0x14DA40F1
        msg.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg.DLC = CANDLC.DLC_AH_16B
        payload = [0x00, len(key) + 2, 0x27, 0x02] + list(key)
        msg.DATA[0:len(payload)] = payload
        self.tx(msg, wait_s=2)

    def io_control(self, did: int, params: List[int]):
        msg = TPCANMsgFD()
        msg.ID = 0x14DA40F1
        msg.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg.DLC = CANDLC.DLC_8H_8B
        msg.DATA[0:8] = [0x07, 0x2F] + [did >> 8, did & 0xFF] + params
        self.tx(msg, wait_s=0.2)