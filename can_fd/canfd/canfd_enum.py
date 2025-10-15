from enum import IntEnum

class CANDLC(IntEnum):
    DLC_0H_0B   = 0x0  # DLC = 0x0 → 0 bytes
    DLC_1H_1B   = 0x1  # DLC = 0x1 → 1 byte
    DLC_2H_2B   = 0x2  # DLC = 0x2 → 2 bytes
    DLC_3H_3B   = 0x3  # DLC = 0x3 → 3 bytes
    DLC_4H_4B   = 0x4  # DLC = 0x4 → 4 bytes
    DLC_5H_5B   = 0x5  # DLC = 0x5 → 5 bytes
    DLC_6H_6B   = 0x6  # DLC = 0x6 → 6 bytes
    DLC_7H_7B   = 0x7  # DLC = 0x7 → 7 bytes
    DLC_8H_8B   = 0x8  # DLC = 0x8 → 8 bytes
    DLC_9H_12B  = 0x9  # DLC = 0x9 → 12 bytes
    DLC_AH_16B  = 0xA  # DLC = 0xA → 16 bytes
    DLC_BH_20B  = 0xB  # DLC = 0xB → 20 bytes
    DLC_CH_24B  = 0xC  # DLC = 0xC → 24 bytes
    DLC_DH_32B  = 0xD  # DLC = 0xD → 32 bytes
    DLC_EH_48B  = 0xE  # DLC = 0xE → 48 bytes



# Map DLC hex values to actual payload byte counts for CAN FD
DLC_2_LEN = {
    0x0: 0,
    0x1: 1,
    0x2: 2,
    0x3: 3,
    0x4: 4,
    0x5: 5,
    0x6: 6,
    0x7: 7,
    0x8: 8,
    0x9: 12,
    0xA: 16,
    0xB: 20,
    0xC: 24,
    0xD: 32,
    0xE: 48,
    0xF: 64
}