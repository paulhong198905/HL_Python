import yaml

class CANDecoder:
    def __init__(self, decode_config_path: str):
        with open(decode_config_path, "r") as f:
            cfg = yaml.safe_load(f)
        self.signal_map = self._parse_config(cfg)

    def _parse_config(self, cfg):
        """Build map: can_id -> list of parameter definitions"""
        signal_map = {}
        for sig in cfg.get("can_signals", []):
            can_id = sig["can_id"]
            signal_map[can_id] = sig["parameters"]
        return signal_map

    def decode(self, can_id: int, data: bytes):
        """Return {signal_name: value} dict for one frame"""
        if can_id not in self.signal_map:
            return {}
        decoded = {}
        for param in self.signal_map[can_id]:
            name = param["name"]
            start_byte = param["start_byte"]
            start_bit = param.get("start_bit", 0)
            bit_length = param["bit_length"]

            raw_val = int.from_bytes(data[start_byte:start_byte+1], "big")
            if start_bit > 0 or bit_length < 8:
                mask = (1 << bit_length) - 1
                raw_val = (raw_val >> start_bit) & mask

            if param["decode_type"] == "stateEncoded":
                decoded[name] = param["values"].get(raw_val, f"UNKNOWN({raw_val})")
            elif param["decode_type"] == "linear":
                a = param["calculation"]["a"]
                b = param["calculation"]["b"]
                decoded[name] = a * raw_val + b
        return decoded
