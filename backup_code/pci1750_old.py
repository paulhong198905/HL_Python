# PCI1750.py

"""
import os
import sys
import logging
from enum import IntEnum
from io_card.Automation.BDaq.InstantDoCtrl import InstantDoCtrl
from io_card.Automation.BDaq.InstantDiCtrl import InstantDiCtrl
from io_card.Automation.BDaq.BDaqApi import BioFailed
from io_card.Enums import DoPort, DoChannelportCount, DoStt

logger = logging.getLogger(__name__)  # module-level logger

def getPCI1750Profilepath():
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    config_dir = os.path.join(base_dir, "Config")
    profilePath = os.path.join(config_dir, "PCI1750_Config_20250818_all_ch_enabled.xml")
    return profilePath

# ============================================================
# CLASS FOR PCI-1750
# ============================================================
class PCI1750:
    def __init__(self, deviceDescription, profilePath=None):
        self.m_deviceDescription = deviceDescription
        self.m_profilePath = profilePath
        self.m_DO_Ctrl = InstantDoCtrl(self.m_deviceDescription)
        self.m_DI_Ctrl = InstantDiCtrl(self.m_deviceDescription)
        self.m_channel_lmt = 15  # different for different card

        if self.m_profilePath:
            self.m_DO_Ctrl.loadProfile = self.m_profilePath
            self.m_DI_Ctrl.loadProfile = self.m_profilePath

        # Dict for DO port state
        self.m_portStates = {
            DoPort.First_8_channel: 0x00,
            DoPort.Second_8_channel: 0x00
        }

        logger.info(f"PCI1750 initialized: {self.m_deviceDescription}")

    # ----------------------
    # Digital Output
    # ----------------------
    def set_DO_channel(self, channel: int, state: DoStt):
        if not (0 <= channel <= self.m_channel_lmt):
            raise ValueError("Channel must be between 0�15")

        port = DoPort.First_8_channel if channel < 8 else DoPort.Second_8_channel
        bit = channel % 8
        mask = 1 << bit

        if state == DoStt.ON:  # ON is requested
            self.m_portStates[port] |= mask
        elif state == DoStt.OFF:
            self.m_portStates[port] &= ~mask
        else:
            raise ValueError("DO set state invalid")

        # Write updated portStates to hardware
        self.m_DO_Ctrl.writeAny(port, 1, [self.m_portStates[port]])

        logger.info(
            f"DO[{channel}] ->"
            f" {'ON' if state else 'OFF'}; "
            f"Port={port}, Value=0x{self.m_portStates[port]:02X}"
        )

    # ----------------------
    # Digital Input
    # ----------------------
    def read_DI_ports(self, channel:int) -> DoStt:

        # Reads a single DI channel.
        # Returns DoStt.ON or DoStt.OFF.

        if not (0 <= channel <= self.m_channel_lmt):
            raise ValueError(f"Channel must be between 0�{self.m_channel_lmt}")

        port = DoPort.First_8_channel if channel < 8 else DoPort.Second_8_channel
        bit = channel % 8

        errCode, data = self.m_DI_Ctrl.readAny(port, 1)

        if BioFailed(errCode):
            logger.error(f"DI read failed on port={port}, err={errCode}")
            return DoStt.OFF  # safe default

        port_val = data[0]
        state = DoStt.ON if (port_val >> bit) & 1 else DoStt.OFF

        logger.info(
            f"DI[{channel}] = {'ON' if state == DoStt.ON else 'OFF'}; "
            f"Port={port}, RawValue=0x{port_val:02X}"
        )

        return state


    def dispose(self):

        Clean up resources.

        self.m_DO_Ctrl.dispose()
        logger.info("PCI1750 disposed")


# ============================================================
# Example Usage
# ============================================================
if __name__ == "__main__":
    # setup logging first

    io_card = PCI1750(deviceDescription="PCI-1750,BID#0", profilePath=getPCI1750Profilepath())
    io_card.set_DO_channel(0, DoStt.ON)
"""