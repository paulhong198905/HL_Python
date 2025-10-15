# hardware/can/base_can_interface.py
from abc import ABC, abstractmethod
from typing import List, Optional

class BaseCANInterface(ABC):
    """Abstract base class for CAN hardware interfaces."""

    @abstractmethod
    def open(self, bitrate: int = 500000, data_bitrate: Optional[int] = None) -> None:
        """Open CAN or CAN FD channel."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close CAN channel."""
        pass

    @abstractmethod
    def send(
        self,
        arbitration_id: int,
        data: List[int],
        is_extended_id: bool = False,
        fd: bool = False,
        brs: bool = False,
        pad_to_min: Optional[int] = None
    ) -> None:
        """Send a CAN or CAN FD frame."""
        pass

    @abstractmethod
    def receive(self, timeout: float = 1.0):
        """Receive a CAN or CAN FD frame."""
        pass