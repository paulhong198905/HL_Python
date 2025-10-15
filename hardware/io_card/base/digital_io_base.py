# digital_io_base.py

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class DigitalIOBase(ABC):
    """Abstract base class for all Digital IO cards."""

    def __init__(self,card_name: str, num_input_channels: int, num_output_channels: int):
        self.m_card_name = card_name
        self.m_num_input_channels = num_input_channels
        self.m_num_output_channels = num_output_channels
        logger.debug(f"{self.m_card_name} initialized (DI={self.m_num_input_channels}, DO={self.m_num_output_channels})")


    # --------------------------
    # Digital Input
    # --------------------------

    @abstractmethod
    def read_single_input(self, channel: int) -> int:
        """Read a single digital input channel (0 or 1)."""
        pass

    @abstractmethod
    def read_all_inputs(self) -> int:
        """
        Read all digital input channels as a bitmask.
        Example: if 8 inputs = [1,0,1,1,0,0,1,0],
        returns int 0b01001101.
        """
        pass

    # --------------------------
    # Digital Output
    # --------------------------
    @abstractmethod
    def write_single_output(self, channel: int, value: int):
        """Write to a single digital output channel (0 or 1)."""
        pass

    @abstractmethod
    def write_all_outputs(self, values: int):
        """
        Write all digital outputs at once using a bitmask.
        Example: values=0b01001101 sets all channels.
        """
        pass
    def info(self) -> str:
        """Return card information string."""
        return f"Card={self.m_card_name}, DI={self.m_num_input_channels}, DO={self.m_num_output_channels}"