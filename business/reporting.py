# business/reporting.py
import os
from datetime import datetime
from typing import Optional
from business.models import TestSummary, TestResult
from common.system_info import get_system_info_report

class ReportGenerator:
    def __init__(self, station: str = "STATIC_IO_TESTER", sw_version: str = "v1.0.0"):
        self.station = station
        self.sw_version = sw_version
    def format_report(
        self,
        summary: TestSummary,
        vin: str,
        harness_pn: str,
        io_card: str = "Advantech PCI-1750"
    ) -> str:
        """Format the test report into a readable string."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        lines = []

        # Overall status banner
        overall_status = "PASS" if summary.failed == 0 else "FAIL"

        banner = "!!! TEST FAILED !!!" if summary.failed > 0 else "*** ALL TESTS PASSED ***"

        lines.append("-" * 59)
        lines.append(" Wiring Harness Test Report")
        lines.append(f" File: LU5201_WH_TEST_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
        lines.append("-" * 59)

        if summary.failed == 0:
            lines.append("###########################################################")
            lines.append("#                     ___  _  __                          #")
            lines.append("#                    / _ \| |/ /                          #")
            lines.append("#                   | | | | ' /                           #")
            lines.append("#                   | |_| | . \                           #")
            lines.append("#                    \___/|_|\_\                          #")
            lines.append("#                                                         #")
            lines.append("###########################################################")
        else:
            lines.append("")





        lines.append("")
        # BIG attention banner
        lines.append(f"================= {banner} =================")
        lines.append("")

        # --- NEW: Add system information report ---
        lines.append(get_system_info_report())

        lines.append(f"Station: {self.station}   SW: {self.sw_version}")
        lines.append(f"VIN: {vin}   Harness PN: {harness_pn}")
        lines.append(f"Date: {timestamp}")
        lines.append("")

        # Compact summary right after banner
        lines.append("---------------- Summary ----------------")
        lines.append(f"Total: {summary.total}   Passed: {summary.passed}   Failed: {summary.failed}")
        lines.append(f"Completion Status: TST_END_NORMAL")


        # Separate summary with detail
        for i in range(5):
            lines.append("")



        # Failures section (only if needed)
        if summary.failed > 0:
            lines.append("---------------- Failures ----------------")
            for res in summary.results:
                if not res.passed:
                    if res.error:
                        lines.append(f"Case: {res.test_id}   Source=DO{res.source_channel}   Error={res.error}")
                    else:
                        detail = []
                        if res.missing_on:
                            detail.append(f"Missing={res.missing_on}")
                        if res.unexpected_on:
                            detail.append(f"Unexpected={res.unexpected_on}")
                        lines.append(
                            f"Case: {res.test_id}   Source=DO{res.source_channel}   "
                            f"Expected={res.expected_targets}   {' '.join(detail)}"
                        )
            lines.append("")
        else:
            lines.append("(No failures detected)")
            lines.append("")

        # Detailed results at the very bottom
        lines.append("--------------------------------------------------")
        lines.append(" Detailed Results (engineer view)")
        lines.append("--------------------------------------------------")
        for res in summary.results:
            status = "PASS" if res.passed else "FAIL"
            mask_str = f"0x{res.measured_mask:04X}" if res.measured_mask >= 0 else "N/A"

            if res.error:
                lines.append(f"[{res.test_id}] {status} | DO{res.source_channel} -> {res.expected_targets}  Error={res.error}")
            else:
                extra = []
                if res.missing_on:
                    extra.append(f"Missing={res.missing_on}")
                if res.unexpected_on:
                    extra.append(f"Unexpected={res.unexpected_on}")
                detail = " ".join(extra) if extra else ""
                lines.append(
                    f"[{res.test_id}] {status} | DO{res.source_channel} -> {res.expected_targets}  "
                    f"Mask={mask_str} {detail}"
                )

        # Footer
        lines.append("--------------------------------------------------")
        lines.append("Test Settings:")
        lines.append(" settle_ms=60   di_num_sample=3   sample_gap_ms=8")
        lines.append(" active_high=True   strict_mode=True")
        lines.append(f" IO Card: {io_card}")
        lines.append("=" * 59)

        return "\n".join(lines)

    def save_report(self, summary: TestSummary, vin: str, harness_pn: str, out_dir: str = "reports") -> str:
        """Save the formatted report to a file and return its path."""
        os.makedirs(out_dir, exist_ok=True)
        filename = f"NDIV01_WH_TEST_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        filepath = os.path.join(out_dir, filename)

        report_str = self.format_report(summary, vin, harness_pn)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_str)

        return filepath

