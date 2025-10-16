# business/can_decoder.py (Completed Configuration Loading)

import yaml
from typing import Dict, Any, List

class CANDecoder:
    def __init__(self, decode_config_path: str):
        """
        Initializes the decoder by loading and parsing the CAN decode YAML file.
        The resulting structure is stored in self.signal_map.
        """
        try:
            with open(decode_config_path, "r") as f:
                cfg = yaml.safe_load(f)
        except Exception as e:
            # Handle File Not Found or YAML parsing errors gracefully
            raise Exception(f"Failed to load CAN decode config file {decode_config_path}: {e}")

        # The core data structure is created and stored here
        self.signal_map: Dict[int, List[Dict[str, Any]]] = self._parse_config(cfg)
        print(f"CANDecoder loaded {len(self.signal_map)} unique CAN IDs from config.")

    def _parse_config(self, cfg: Dict[str, Any]) -> Dict[int, List[Dict[str, Any]]]:
        """
        Parses the loaded configuration dictionary into a map keyed by CAN ID.
        This allows for fast lookup during the decoding process.
        """
        signal_map = {}

        # Iterate over the top-level 'can_signals' list in the YAML
        for message in cfg.get("can_signals", []):
            can_id = message["can_id"]
            # Store the list of all parameters/signals defined for this CAN ID
            signal_map[can_id] = message.get("parameters", [])

        return signal_map



    def _extract_bits(self, data: bytes, start_byte: int, start_bit: int, length: int) -> int:
        """
        Extracts the raw integer value of a bit field from the message data.
        Assumes Little-Endian or Big-Endian byte order based on system/library default,
        but bit field extraction is done per byte.
        """
        if start_byte >= len(data):
            return 0

        # Get the target byte
        byte_val = data[start_byte]

        # Create a mask for the bit length
        mask = (1 << length) - 1

        # Shift the byte value right by the start bit position, then apply the mask
        return (byte_val >> start_bit) & mask

    def decode(self, can_id: int, data: bytes) -> Dict[str, Any]:
        """Decodes all signals within a single raw CAN message."""
        decoded_signals = {}

        # Fast lookup of signals defined for this CAN ID
        signals_to_decode = self.signal_map.get(can_id)
        if not signals_to_decode:
            return decoded_signals

        for signal_def in signals_to_decode:
            name = signal_def['name']

            # 1. Extract the raw integer value
            raw_value = self._extract_bits(
                data,
                signal_def['start_byte'],
                signal_def.get('start_bit', 0),  # Use 0 as default if not specified
                signal_def['bit_length']
            )

            # 2. Apply decoding based on type
            decoded_value = raw_value
            decode_type = signal_def['decode_type']

            if decode_type == "stateEncoded":
                # Apply state mapping (e.g., 2 -> "RUN")
                decoded_value = signal_def.get('values', {}).get(raw_value, f"UNKNOWN({raw_value})")

            elif decode_type == "linear":
                # Apply scaling and offset
                calc = signal_def.get('calculation', {})
                a = calc.get('a', 1.0)
                b = calc.get('b', 0.0)
                decoded_value = raw_value * a + b

            # Store the result
            decoded_signals[name] = decoded_value

        return decoded_signals