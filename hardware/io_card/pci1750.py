# hardware/io_card/pci1750.PY
import logging
import os
import sys

from hardware.io_card.base.digital_io_base import DigitalIOBase
from hardware.io_card.vendor.yanhua.Automation.BDaq.BDaqApi import BioFailed
from hardware.io_card.vendor.yanhua.Automation.BDaq.BDaqApi import ErrorCode
from hardware.io_card.vendor.yanhua.Automation.BDaq.InstantDiCtrl import InstantDiCtrl
from hardware.io_card.vendor.yanhua.Automation.BDaq.InstantDoCtrl import InstantDoCtrl

logger = logging.getLogger(__name__)

# --------------------------
# Helper function
# --------------------------
def getPCI1750ProfilePath(profileName:str) -> str:
    """Return the XML profile path for PCI1750."""
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    config_dir = os.path.join(base_dir, "config")
    return os.path.join(config_dir, profileName)
    # return os.path.join(config_dir, "PCI1750_Config_20250818_all_ch_enabled.xml")


# --------------------------
# PCI_1750 class
# --------------------------
class PCI_1750(DigitalIOBase):
    """PCI-1750 Digital IO card implementation (Yanhua version)."""

    def __init__(self, profileName: str, deviceDescription: str = "PCI-1750,BID#0"):
        super().__init__(card_name=deviceDescription, num_input_channels=16, num_output_channels=16)
        # current default profileName = PCI1750_Config_20250818_all_ch_enabled.xml

        # 1. Initialize all IO controller handles to None BEFORE the try block.
        # self.m_di = None
        # self.m_do = None

        self.m_num_input_channels = 16  # Number of DI channels
        self.m_num_output_channels = 16  # Number of DO channels

        self.deviceDescription = deviceDescription
        self.profilePath = getPCI1750ProfilePath(profileName)

        try:
            # Initialize hardware
            self.m_di = InstantDiCtrl()
            self.m_di.selectedDevice = self.deviceDescription

            self.m_do = InstantDoCtrl()
            self.m_do.selectedDevice = self.deviceDescription

            # Load profile if available
            if self.profilePath:
                self.m_di.loadProfile = self.profilePath
                self.m_do.loadProfile = self.profilePath

            logger.info(f"{self.deviceDescription} connected, profile: {self.profilePath}")


        except Exception as e:  # <-- CHANGE 'BioFailed' to 'Exception'
            logger.error(f"Failed to initialize {self.deviceDescription}: {e}")


    # --------------------------
    # Digital Input
    # --------------------------
    def read_single_input(self, channel: int) -> int:
        """Read a single digital input channel (0–15)."""
        err, value = self.m_di.readBit(channel // 8, channel % 8)
        if err != ErrorCode.Success:
            logger.error(f"read_single_input failed: {err}")
            return -1
        return value

    def read_all_inputs(self) -> int:
        """Read all digital inputs as a 16-bit bitmask."""
        err, data = self.m_di.readAny(0, 2)  # Read 2 ports (16 channels)
        if err != ErrorCode.Success:
            logger.error(f"read_all_inputs failed: {err}")
            return -1

        inputs = (data[1] << 8) | data[0]

        # Log both formats with prefixes
        logger.debug(f"Inputs (bitmask): 0x{inputs:04X}")   # Hex, zero-padded, with 0x
        logger.debug(f"Inputs (binary):  0b{inputs:016b}")  # Binary, 16 bits, with 0b

        return inputs

    # --------------------------
    # Digital Output
    # --------------------------
    def write_single_output(self, channel: int, value: int) -> bool:
        """Write to a single digital output channel (0–15)."""
        err = self.m_do.writeBit(channel // 8, channel % 8, value)
        if err != ErrorCode.Success:
            logger.error(f"write_single_output failed: {err}")
            return False
        return True

    def write_all_outputs(self, values: int) -> bool:
        """Write bitmask to all outputs (16-bit)."""
        data = [values & 0xFF, (values >> 8) & 0xFF]
        err = self.m_do.writeAny(0, 2, data)
        if err != ErrorCode.Success:
            logger.error(f"write_all_outputs failed: {err}")
            return False

        # Log outputs in hex and binary
        logger.debug(f"Outputs (bitmask): 0x{values:04X}")
        logger.debug(f"Outputs (binary): 0b{values:016b}")

        return True

    def close(self):
        if self.m_di:
            self.m_di.cleanup()
        if self.m_do:
            self.m_do.cleanup()
        logger.info(f"{self.deviceDescription} released / closed.")
