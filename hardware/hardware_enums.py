from enum import Enum


class PCANCh(str, Enum):
    PCAN_USB_BUS_1 = "PCAN_USBBUS1"
    PCAN_USB_BUS_2 = "PCAN_USBBUS2"
    PCAN_USB_BUS_3 = "PCAN_USBBUS3"

    PCAN_PCI_BUS_1 = "PCAN_PCIBUS1"
    PCAN_PCI_BUS_2 = "PCAN_PCIBUS2"
    PCAN_PCI_BUS_3 = "PCAN_PCIBUS3"

    # Default channel (change here if needed globally)
    DEFAULT_PCAN_CH = PCAN_USB_BUS_1  # default channel



class Baudrate(int, Enum):
    _500kbps = 500_000
    _2mbps   = 2_000_000
    _5mbps   = 5_000_000


class CANFDDLC(Enum):
    """Mapping of CAN FD DLC codes to payload byte lengths."""
    DLC_0  = 0
    DLC_1  = 1
    DLC_2  = 2
    DLC_3  = 3
    DLC_4  = 4
    DLC_5  = 5
    DLC_6  = 6
    DLC_7  = 7
    DLC_8  = 8
    DLC_12 = 12
    DLC_16 = 16
    DLC_20 = 20
    DLC_24 = 24
    DLC_32 = 32
    DLC_48 = 48
    DLC_64 = 64

    @classmethod
    def from_payload_length(cls, length: int) -> "CANFDDLC":
        """
        Get the minimal DLC that can hold the given payload length.
        Mirrors CAN FD DLC mapping rules.
        """
        if length <= 8:
            return cls(length)  # DLC_0 … DLC_8
        elif length <= 12:
            return cls.DLC_12
        elif length <= 16:
            return cls.DLC_16
        elif length <= 20:
            return cls.DLC_20
        elif length <= 24:
            return cls.DLC_24
        elif length <= 32:
            return cls.DLC_32
        elif length <= 48:
            return cls.DLC_48
        else:
            return cls.DLC_64

    @property
    def byte_length(self) -> int:
        """Return the number of bytes this DLC represents."""
        return self.value

class PendingDuration(float, Enum):
    _1ms    = 0.001
    _2ms    = 0.002
    _3ms    = 0.003
    _4ms    = 0.004
    _5ms    = 0.005
    _6ms    = 0.006
    _7ms    = 0.007
    _8ms    = 0.008
    _9ms    = 0.009
    _10ms   = 0.01
    _25ms   = 0.025
    _30ms   = 0.030
    _40ms   = 0.040
    _50ms   = 0.05
    _100ms  = 0.1
    _200ms  = 0.2
    _250ms  = 0.25
    _500ms  = 0.5
    _1000ms = 1.0
    _2000ms = 1.0
    _2500ms = 2.5
    _5000ms = 5.0

    DEFAULT = 0.01

    def __float__(self) -> float:
        return self.value