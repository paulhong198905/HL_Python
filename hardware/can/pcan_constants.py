# hardware/can/pcan_constants.py
from hardware.can.PCANBasic import (
    PCAN_MESSAGE_STANDARD,
    PCAN_MESSAGE_RTR,
    PCAN_MESSAGE_EXTENDED,
    PCAN_MESSAGE_FD,
    PCAN_MESSAGE_BRS,
    PCAN_MESSAGE_ESI,
    PCAN_MESSAGE_ECHO,
    PCAN_MESSAGE_ERRFRAME,
    PCAN_MESSAGE_STATUS,
    PCAN_PARAMETER_ON,
    PCAN_ALLOW_ECHO_FRAMES,
    PCAN_ERROR_QRCVEMPTY,
    PCAN_USBBUS1,
    PCAN_USBBUS2,
    PCAN_PCIBUS1,
    TPCANHandle,
    PCAN_ERROR_OK,
)


# ---- Normalize to Python ints ----
PCAN_MESSAGE_STANDARD = int(PCAN_MESSAGE_STANDARD.value)
PCAN_MESSAGE_RTR      = int(PCAN_MESSAGE_RTR.value)
PCAN_MESSAGE_EXTENDED = int(PCAN_MESSAGE_EXTENDED.value)
PCAN_MESSAGE_FD       = int(PCAN_MESSAGE_FD.value)
PCAN_MESSAGE_BRS      = int(PCAN_MESSAGE_BRS.value)
PCAN_MESSAGE_ESI      = int(PCAN_MESSAGE_ESI.value)
PCAN_MESSAGE_ECHO     = int(PCAN_MESSAGE_ECHO.value)
PCAN_MESSAGE_ERRFRAME = int(PCAN_MESSAGE_ERRFRAME.value)
PCAN_MESSAGE_STATUS   = int(PCAN_MESSAGE_STATUS.value)
PCAN_ERROR_OK         = PCAN_ERROR_OK
# PCAN_ERROR_QRCVEMPTY  = PCAN_ERROR_QRCVEMPTY



# ---- Bitrate presets ----
bitrate_fd_500K_2Mb = (
    b"f_clock=80000000, nom_brp=10, nom_tseg1=12, nom_tseg2=3, nom_sjw=1, "
    b"data_brp=4, data_tseg1=7, data_tseg2=2, data_sjw=1"
)

# ---- Channel enum ----
from enum import Enum
class PCANCh(Enum):
    USB1 = PCAN_USBBUS1.value
    USB2 = PCAN_USBBUS2.value
    PCI1 = PCAN_PCIBUS1.value

PCANCh.default = PCANCh.USB1.value


__all__ = [
    "PCAN_MESSAGE_STANDARD",
    "PCAN_MESSAGE_RTR",
    "PCAN_MESSAGE_EXTENDED",
    "PCAN_MESSAGE_FD",
    "PCAN_MESSAGE_BRS",
    "PCAN_MESSAGE_ESI",
    "PCAN_MESSAGE_ECHO",
    "PCAN_MESSAGE_ERRFRAME",
    "PCAN_MESSAGE_STATUS",
    "PCAN_PARAMETER_ON",
    "PCAN_ALLOW_ECHO_FRAMES",
    "PCAN_ERROR_QRCVEMPTY",
    "bitrate_fd_500K_2Mb",
    "PCANCh",
    "PCAN_ERROR_OK"
]