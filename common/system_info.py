# common/system_info.py
import platform
import socket
import getpass
from datetime import datetime

def collect_system_info() -> dict:
    """Collect general system information."""
    info = {
        "Host": socket.gethostname(),
        "User": getpass.getuser(),
        "OS": f"{platform.system()} {platform.release()} ({platform.version()})",
        "Python": platform.python_version(),
        # "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        # "Architecture": platform.architecture()[0] + " " + platform.win32_ver()[0],
    }
    return info

def format_system_info(info: dict) -> str:
    """Format system info into a report-friendly string."""
    lines = [
        "---------------- System Information ----------------",
    ]
    for key, value in info.items():
        lines.append(f"{key}: {value}")
    lines.append("---------------------------------------------------")
    return "\n".join(lines)

def get_system_info_report() -> str:
    """Collect and format system info in one call."""
    info = collect_system_info()
    return format_system_info(info)
