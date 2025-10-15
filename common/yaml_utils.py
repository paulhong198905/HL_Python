# common/yaml_utils.py
import logging
from typing import List
from pathlib import Path
import yaml

# Updated import for the business module
from business.wiring_harness_tester import WiringHarnessTestCase

logger = logging.getLogger(__name__)

def read_yaml_wh_cases(yaml_path: Path) -> List[WiringHarnessTestCase]:
    """
    Load your YAML and convert 'loops' into WiringHarnessTestCase objects.
    """

    with open(yaml_path, "r") as f:
        y = yaml.safe_load(f)

    loops = y.get("loops", [])
    cases = [WiringHarnessTestCase.from_yaml(d) for d in loops]
    logger.info(f"Loaded {len(cases)} wiring-harness cases from {yaml_path}")
    return cases