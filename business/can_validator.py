import yaml

class Validator:
    def __init__(self, validation_config_path: str):
        with open(validation_config_path, "r") as f:
            cfg = yaml.safe_load(f)
        self.tests = cfg.get("tests", [])
        self.state_history = {}  # signal_name -> set of seen values
        self.last_value = {}     # signal_name -> last seen value

    # def feed(self, signal_name, value):
    #     """Store new signal observation"""
    #     self.state_history.setdefault(signal_name, set()).add(value)
    #     self.last_value[signal_name] = value

    def feed(self, signal_name, value):

        if signal_name not in self.state_history:
            self.state_history[signal_name] = set()

        signal_set = self.state_history[signal_name]
        signal_set.add(value)

        self.last_value[signal_name] = value



    def validate_all(self):
        """Run all tests and return results, aggregating all failure reasons with clear labels."""
        results = []

        for test in self.tests:
            sig = test["signal"]
            result = {"test": test["name"], "pass": True, "reason": "PASS"} # Initialize to PASS

            # Use a list to hold all failure messages for this specific test
            failure_reasons = []

            # --- 1. Required States Check ---
            if "required_states" in test:
                required = set(test["required_states"])
                seen = self.state_history.get(sig, set())
                missing = required - seen
                if missing:
                    # Clear Label and detailed set info
                    failure_reasons.append(f"State History Failure: Missing required states: {sorted(list(missing))}")

            # --- 2. Require Final Check ---
            if "require_final" in test:
                final = test["require_final"]
                current_final = self.last_value.get(sig)
                if current_final != final:
                    # Clear Label and observed vs. expected info
                    failure_reasons.append(f"Final State Failure: Expected {final}, but found {current_final}")

            # --- 3. Range Check ---
            if "range" in test:
                minv, maxv = test["range"]["min"], test["range"]["max"]
                val = self.last_value.get(sig)

                is_out_of_range = False
                reason_message = ""

                if val is None:
                    is_out_of_range = True
                    reason_message = "Range Failure: Signal value is missing (None)."
                elif not (minv <= val <= maxv):
                    is_out_of_range = True
                    reason_message = f"Range Failure: Value {val} is not within [{minv}, {maxv}]"

                if is_out_of_range:
                    failure_reasons.append(reason_message)

            # --- Finalize Result ---
            if failure_reasons:
                result["pass"] = False
                # Join all failure reasons with a newline character (\n) for readability
                result["reason"] = ";".join(failure_reasons)
            else:
                result["reason"] = "PASS" # Keep explicit PASS status

            results.append(result)
        return results