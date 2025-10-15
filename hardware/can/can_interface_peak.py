# hardware/can/can_interface_peak.py

import can
from typing import List, Optional
from hardware.can.base_can_interface import BaseCANInterface
from hardware.hardware_enums import Baudrate, CANFDDLC
from hardware.can.pcan_constants import PCANCh

from can.bit_timing import BitTimingFd
from can.interfaces.pcan import PcanBus


class CANInterfacePeak(BaseCANInterface):
    """PEAK PCAN implementation of BaseCANInterface supporting CAN and CAN FD."""

    def __init__(self, channel: str = PCANCh.DEFAULT_PCAN_CH):
        self.channel: str = channel
        self.bus: Optional[can.Bus] = None

    def open(
        self,
        bitrate: int = Baudrate._500kbps,
        data_bitrate: Optional[int] = None,
        fd_timing: Optional[BitTimingFd] = None,
        bitrate_switch: bool = True
    ) -> None:
        """Open a CAN or CAN FD channel."""
        if data_bitrate:  # CAN FD
            if fd_timing is None:
                # Default CAN FD timing
                fd_timing = BitTimingFd(
                    f_clock=80_000_000,
                    nom_brp=10,
                    nom_tseg1=12,
                    nom_tseg2=3,
                    nom_sjw=1,
                    data_brp=4,
                    data_tseg1=7,
                    data_tseg2=2,
                    data_sjw=1
                )

            self.bus = PcanBus(
                channel=self.channel,
                interface="pcan",
                fd=True,
                f_clock=80_000_000,
                nom_bitrate=bitrate,
                data_bitrate=data_bitrate,
                timing=fd_timing,
                bitrate_switch=bitrate_switch
            )
        else:  # Classic CAN
            self.bus = PcanBus(
                channel=self.channel,
                interface="pcan",
                bitrate=bitrate
            )

    def close(self) -> None:
        """Close the CAN channel safely."""
        if self.bus:
            self.bus.shutdown()
            self.bus = None

    def send(
        self,
        arbitration_id: int,
        data: List[int],
        fd: bool = False,
        is_extended_id: bool = False,
        brs: bool = False,
        pad_to_min: Optional[CANFDDLC] = None
    ) -> None:
        """
        Send a CAN or CAN FD frame with proper DLC calculation.

        :param arbitration_id: CAN ID
        :param data: Payload bytes
        :param is_extended_id: True for 29-bit CAN ID
        :param fd: True for CAN FD frame
        :param brs: True to enable bit rate switching for CAN FD
        :param pad_to_min: Optional minimum payload length (pads with 0x00 if shorter)
        """
        if self.bus is None:
            raise RuntimeError("CAN bus not opened")

        payload = list(data)

        # Apply padding if requested
        if pad_to_min is not None:
            pad_length = pad_to_min.byte_length
            if len(payload) < pad_length:
                payload.extend([0x00] * (pad_length - len(payload)))

        # Determine DLC
        if fd:
            dlc_enum = CANFDDLC.from_payload_length(len(payload))
            dlc = dlc_enum.value
        else:
            dlc = len(payload)

        msg = can.Message(
            arbitration_id=arbitration_id,
            is_extended_id=is_extended_id,
            data=payload,
            is_fd=fd,
            bitrate_switch=brs,
            dlc=dlc
        )

        self.bus.send(msg)

    def receive(self, timeout: float = 1.0) -> Optional[can.Message]:
        """Receive a CAN or CAN FD frame."""
        if self.bus is None:
            raise RuntimeError("CAN bus not opened")
        return self.bus.recv(timeout=timeout)
