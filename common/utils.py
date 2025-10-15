# common/utils.py
import sys
from pathlib import Path

import yaml


# ============================================================
# Path / File Utilities
# ============================================================

def get_exe_dir() -> Path:
    """
    Return the directory where the current script or executable resides.
    Works for both normal Python scripts and PyInstaller executables.`
    """
    if getattr(sys, "frozen", False):
        # Running in PyInstaller bundle
        exe_path = Path(sys.executable)
    else:
        # Normal Python script
        exe_path = Path(sys.argv[0]).resolve()
    return exe_path.parent


def join_with_exe_dir(*paths: str) -> Path:
    """
    Join one or more relative paths to the exe/script directory.

    Usage:
        join_with_exe_dir("Config", "CKPT_WH_PN12345678_V1.yaml")
    """
    return get_exe_dir().joinpath(*paths)



def ensure_path_exists(path: Path, create_dir: bool = False) -> Path:
    """
    Validate that a path exists. Optionally create directories if they don't exist.
    Raises FileNotFoundError if path does not exist and create_dir=False.
    """
    if create_dir:
        path.mkdir(parents=True, exist_ok=True)
    elif not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    return path

# ============================================================
# YAML Utilities
# ============================================================

def read_yaml_file(yaml_file: Path) -> dict:
    """
    Read a YAML file and return its content as a dictionary.
    Accepts Path or string.
    Raises exceptions if file does not exist or is invalid.
    """
    yaml_file = Path(yaml_file)
    if not yaml_file.is_file():
        raise FileNotFoundError(f"YAML file not found: {yaml_file}")
    with yaml_file.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml_file(yaml_file: Path, data: dict, sort_keys: bool = False):
    """
    Write a dictionary to a YAML file.
    Accepts Path or string.
    """
    yaml_file = Path(yaml_file)
    with yaml_file.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=sort_keys, allow_unicode=True)