# business/workers/wh_test_worker.py

from PySide6.QtCore import QThread, Signal
import logging
from typing import Dict, Any, List


from hardware.io_card.pci1750 import PCI_1750
from business.wiring_harness_tester import WiringHarnessTester
from common.yaml_utils import read_yaml_wh_cases
from common.utils import join_with_exe_dir
from business.models import TestSummary, TestResult  # Make sure TestResult is imported

logger = logging.getLogger(__name__)

# Define the constants for the PCI card profile name
PCI_PROFILE_NAME = "PCI1750_Config.xml"


class WhTestWorker(QThread):
    # Signal emitted when the entire test is finished
    # Arguments: (success_bool, result_message_string, worker_id)
    sig_test_finished = Signal(bool, str, str)

    # Optional: progress signal for status bar updates
    sig_progress_updated = Signal(str, int, str)  # (message, percentage, worker_id)

    def __init__(self, config_filepath: str, worker_id: str, parent=None):
        super().__init__(parent)
        self.config_filepath = config_filepath
        self.worker_id = worker_id  # Should be 'HARDWARE_TEST' or similar
        self.is_running = True

    def run(self):
        logger.info(f"[{self.worker_id}] Worker started. Config file: {self.config_filepath}")

        io_card = None

        # 1. Update progress on main thread
        self.sig_progress_updated.emit("WH Test: Initializing Hardware...", 1, self.worker_id)

        try:
            # 2. Initialize hardware handle (BLOCKING I/O)
            io_card = PCI_1750(profileName=PCI_PROFILE_NAME)

            # 3. Load YAML test cases (BLOCKING I/O)
            self.sig_progress_updated.emit("WH Test: Loading test cases...", 2, self.worker_id)
            cases = read_yaml_wh_cases(self.config_filepath)

            if not cases:
                raise Exception("No wiring harness test cases loaded.")

            # 4. Create tester & run tests
            self.sig_progress_updated.emit(f"WH Test: Running {len(cases)} loops...", 3, self.worker_id)

            tester = WiringHarnessTester(io_card=io_card)
            summary: TestSummary = tester.run_all(cases)  # returns TestSummary object
            # 5. Determine result string and capture failed circuits
            passed_bool = not summary.failed
            failed_circuits: List[int] = []

            # ----------------------------------------------------
            # Base Result Message (Always set this first)
            # ----------------------------------------------------
            result_msg = f"WH Test: {summary.passed}/{summary.total} Passed.\n"

            if passed_bool:
                logger.info(f"[{self.worker_id}] Test PASS.")
                color_flag = 'success'
            else:
                # Test FAILED: Identify faulty circuits
                for result in summary.results:
                    # Check for explicit failure and ensure circuit_Num exists
                    if not result.passed and result.circuit_Num is not None:
                        failed_circuits.append(result.circuit_Num)

                # Format the list of failed circuits
                circuit_list_str = ", ".join(map(str, failed_circuits))

                # Append the detailed failure list to the result message for the UI/Controller
                result_msg += f" FAILED Circuits: [{circuit_list_str}]"

                # Update the log message with the extended error details
                extended_error_msg = f"Test FAIL. {summary.failed} loops failed. Circuits: [{circuit_list_str}]"
                logger.error(f"[{self.worker_id}] {extended_error_msg}")

                color_flag = 'fail'

            # 6. Emit final result
            self.sig_test_finished.emit(passed_bool, result_msg, self.worker_id)

        except Exception as e:
            logger.error(f"[{self.worker_id}] Worker failed during execution: {e}", exc_info=True)
            self.sig_test_finished.emit(False, f"WH Test ERROR: {e}", self.worker_id)
            color_flag = 'fail'

        finally:
            # 7. Clean up hardware
            if io_card is not None:
                io_card.close()
                logger.debug(f"[{self.worker_id}] IO card closed.")