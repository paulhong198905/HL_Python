# tests/test_io/test_io.py

import logging
from hardware.io_card.pci1750 import PCI_1750
from business.wiring_harness_tester import WiringHarnessTester
from business.models import TestSummary
from common.yaml_utils import read_yaml_wh_cases
from common.utils import join_with_exe_dir

logger = logging.getLogger(__name__)


def io_test_auto():
    logger.debug("io_test_auto() started.")

    io_card = None
    try:
        # --------------------------
        # 1) Initialize hardware handle
        # --------------------------
        io_card = PCI_1750(profileName="PCI1750_Config.xml")

        # --------------------------
        # 2) Load YAML test cases
        # --------------------------
        yaml_path = join_with_exe_dir("config", "CKPT_WH_PN12345678_V1.yaml")
        cases = read_yaml_wh_cases(yaml_path)

        # --------------------------
        # 3) Create tester & run tests
        # --------------------------
        tester = WiringHarnessTester(
            io_card=io_card,
            settle_ms=80,
            di_num_sample=3,
            sample_gap_ms=10,
            require_only_targets=True,  # set False to allow extra highs
            active_high=True
        )
        summary: TestSummary = tester.run_all(cases)  # returns TestSummary object

        # --------------------------
        # 4) React to results
        # --------------------------
        if summary.failed:
            logger.error(f"{summary.failed} wiring-harness cases failed.")
            logger.info(f"{summary.passed} cases passed.")  # optional additional info
        else:
            logger.info("All wiring-harness cases passed.")

    except Exception as e:
        logger.error(f"io_test_auto failed: {e}", exc_info=True)

    finally:
        if io_card is not None:
            io_card.close()
            logger.debug("IO card closed successfully.")


def IOTestManual():
    """Automatic demo test for PCI-1750."""
    logger.debug("io_test_auto() started.")

    io_card = None

    try:
        # Initialize PCI-1750 card
        io_card = PCI_1750(profileName="PCI1750_Config.xml")

        # --------------------------
        # Read all digital inputs
        # --------------------------
        inputs = io_card.read_all_inputs()
        if inputs >= 0:
            logger.info(f"Inputs (bitmask): 0x{inputs:04X}")
            logger.info(f"Inputs (binary): 0b{inputs:016b}")
            # Detailed per-channel log
            # for ch in range(16):
            #     state = (inputs >> ch) & 1
            #     logger.info(f"  Input channel {ch:02d}: {state}")

        # --------------------------
        # Write outputs (demo pattern)
        # --------------------------
        demo_pattern = 0x0101
        success = io_card.write_all_outputs(demo_pattern)
        if success:
            logger.info(f"Outputs written with demo pattern 0x{demo_pattern:04X}")

        # --------------------------
        # Read all digital inputs
        # --------------------------
        inputs = io_card.read_all_inputs()
        if inputs >= 0:
            logger.info(f"Inputs (bitmask): 0x{inputs:04X}")
            logger.info(f"Inputs (binary): 0b{inputs:016b}")
            # Detailed per-channel log
            # for ch in range(16):
            #     state = (inputs >> ch) & 1
            #     logger.info(f"  Input channel {ch:02d}: {state}")



    except Exception as e:
        logger.error(f"io_test_auto failed: {e}", exc_info=True)
    finally:
        if io_card is not None:
            io_card.close()

