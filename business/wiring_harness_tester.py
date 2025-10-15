# business/wiring_harness_tester.py
import logging
import time
from datetime import datetime
from typing import List

from business.models import TestResult, WiringHarnessTestCase, TestSummary
from business.reporting import ReportGenerator

logger = logging.getLogger(__name__)


# --------------------------
# The runner that executes cases on a DigitalIOBase
# --------------------------
class WiringHarnessTester:
    def __init__(
            self,
            io_card,  # DigitalIOBase (e.g., PCI_1750)
            settle_ms: int = 60,  # wait after DO change
            di_num_sample: int = 3,  # DI samples for stability
            sample_gap_ms: int = 8,  # gap between samples
            require_only_targets: bool = True,  # strict mode: only targets may be ON
            active_high: bool = True,  # polarity for DO/DI logic
    ):
        self.io = io_card
        self.settle_ms = settle_ms
        self.di_num_sample = max(1, di_num_sample)
        self.sample_gap_ms = sample_gap_ms
        self.require_only_targets = require_only_targets
        self.active_high = active_high

    # ---------- helpers ----------
    @staticmethod
    def _fmt_mask(mask: int) -> str:
        """
        Format mask as hex + binary string for readability.
        Example: 0x00F3 (0000000011110011)
        """
        binary_str = f"{mask:016b}"  # always 16-bit
        return f"0x{mask:04X} = 0b{binary_str}"

    @staticmethod
    def _sleep_ms(ms: int):
        time.sleep(ms / 1000.0)

    def _read_stable_inputs(self) -> int:
        """
        Read DI multiple times and use majority-vote per-bit to produce a stable mask.
        Returns:
          - >=0 : 16-bit mask of inputs (bit N => channel N is considered ON)
          - -1   : read error occurred
        """
        # counts per bit
        counts = [0] * self.io.m_num_input_channels  # → [0, 0, 0, 0, 0]

        for i in range(self.di_num_sample):
            m = self.io.read_all_inputs()
            if m < 0:
                # read error
                logger.error(f"Underlying IO read_all_inputs returned error on attempt[{i}] %d")
                return -1
            for ch in range(self.io.m_num_input_channels):
                if (m >> ch) & 1:
                    # shifts the mask m right by ch bits, then checks if the lowest bit = 1;
                    # 1 → channel is ON
                    # 0 → channel is OFF
                    counts[ch] += 1
            if i < self.di_num_sample - 1:
                self._sleep_ms(self.sample_gap_ms)

        # majority threshold
        threshold = (self.di_num_sample // 2) + 1
        mask = 0
        for ch in range(self.io.m_num_input_channels):
            if counts[ch] >= threshold:
                mask |= (1 << ch)

        return mask

    # ---------- core flow ----------
    def run_case(self, case: WiringHarnessTestCase) -> TestResult:
        logger.info(f"-------------------------------------------------")
        logger.info(f"*****     TestCase for {case.id} from YAML configFile     *****")
        logger.info(f"Expected wiring: DO{case.source} -> DI{case.targets}")
        logger.info(f"Test type: {case.test_type}")
        if case.note:
            logger.info(f"Note: {case.note}")
        logger.info(f"-------------------------------------------------")

        # 1) Drive source ON (respect polarity)
        on_val = 1 if self.active_high else 0
        off_val = 0 if self.active_high else 1

        # Attempt write ON; if fails, return immediately
        ret = self.io.write_single_output(case.source, on_val)
        if not ret:
            logger.error(f"[{case.id}] Failed to drive DO{case.source} ON")
            return TestResult(
                test_id=case.id,
                timestamp=datetime.now().isoformat(timespec="seconds"),
                source_channel=case.source,
                expected_targets=case.targets,
                measured_mask=-1,
                missing_on=[],
                unexpected_on=[],
                passed=False,
                circuit_Num=case.circuit_Num,
                PN=case.PN,
                note=case.note,
                error="do_write_failed",
            )

        # Ensure DO is turned OFF even on exceptions
        inputs_mask = -1
        try:
            self._sleep_ms(self.settle_ms)
            # 2) Read DI (stable, majority vote)
            inputs_mask = self._read_stable_inputs()
        finally:
            # 3) Safety: turn DO back OFF (best effort)
            try:
                self.io.write_single_output(case.source, off_val)
            except Exception as e:
                logger.warning(f"[{case.id}] Failed to set DO{case.source} OFF in finally: {e}")

        if inputs_mask < 0:
            logger.error(f"[{case.id}] DI read failed")
            return TestResult(
                test_id=case.id,
                timestamp=datetime.now().isoformat(timespec="seconds"),
                source_channel=case.source,
                expected_targets=case.targets,
                measured_mask=-1,
                missing_on=[],
                unexpected_on=[],
                passed=False,
                circuit_Num=case.circuit_Num,
                PN=case.PN,
                note=case.note,
                error="di_read_failed",
            )

        # Log masks
        logger.info(f"WH_Test_ID=[{case.id}], DI state: {self._fmt_mask(inputs_mask)}")

        # Detailed per-channel (debug)
        active_channels = [ch for ch in range(self.io.m_num_input_channels) if (inputs_mask >> ch) & 1]
        logger.debug(f"[{case.id}] Active DI channels: {active_channels}")

        # 4) Evaluate: compute missing and unexpected channels
        expected_on = set(case.targets)
        on_channels = active_channels
        unexpected_on = [ch for ch in on_channels if ch not in expected_on]
        missing_on = [ch for ch in expected_on if ((inputs_mask >> ch) & 1) == 0]

        if self.require_only_targets:
            passed = (len(missing_on) == 0) and (len(unexpected_on) == 0)
        else:
            passed = (len(missing_on) == 0)

        if missing_on:
            logger.error(f"[{case.id}] Missing HIGH on DI channels: {missing_on}")
        if self.require_only_targets and unexpected_on:
            logger.error(f"[{case.id}] Unexpected HIGH on DI channels: {unexpected_on}")

        if passed:
            logger.info(f"[{case.id}] PASS")
        else:
            logger.error(f"[{case.id}] FAIL")

        return TestResult(
            test_id=case.id,
            timestamp=datetime.now().isoformat(timespec="seconds"),
            source_channel=case.source,
            expected_targets=case.targets,
            measured_mask=inputs_mask,
            missing_on=missing_on,
            unexpected_on=unexpected_on,
            passed=passed,
            circuit_Num=case.circuit_Num,
            PN=case.PN,
            note=case.note,
        )

    def run_all(self, cases: List[WiringHarnessTestCase]) -> TestSummary:
        """Run all cases; return a summary and detailed results."""
        results = []
        passed_count = 0
        total = len(cases)

        # Try to force all outputs OFF before starting
        try:
            ok = self.io.write_all_outputs(0)
            if not ok:
                logger.warning("Could not force DO all OFF at start (driver returned False)")
        except Exception as ex:
            logger.warning("Could not force DO all OFF at start: %s", ex)

        for case in cases:
            res = self.run_case(case)
            results.append(res)
            if res.passed:
                passed_count += 1

        # Try to force all outputs OFF at the end
        try:
            ok = self.io.write_all_outputs(0)
            if not ok:
                logger.warning("Could not force DO all OFF at end (driver returned False)")
        except Exception as ex:
            logger.warning("Could not force DO all OFF at end: %s", ex)

        summary = TestSummary(
            total=total,
            passed=passed_count,
            failed=total - passed_count,
            results=results,
        )

        reporter = ReportGenerator(station="STATIC_IO_TESTER", sw_version="v1.0.0")
        path = reporter.save_report(summary, vin="LSGMF888888888888", harness_pn="12345678")

        logger.info(f"=== WH Summary: {summary.passed}/{summary.total} passed ===")
        return summary
