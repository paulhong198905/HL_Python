# business/models.py
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime
import json


@dataclass
class TestResult:
    test_id: str
    timestamp: str
    source_channel: int
    expected_targets: List[int]
    measured_mask: int
    missing_on: List[int]
    unexpected_on: List[int]
    passed: bool
    # Optional below
    circuit_Num: Optional[int] = None
    PN: Optional[List[int]] = None
    note: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), indent=indent)

@dataclass
class TestSummary:
    total: int
    passed: int
    failed: int
    results: List[TestResult]

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "results": [r.to_dict() for r in self.results],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

@dataclass
class WiringHarnessTestCase:
    id: str
    source: int
    targets: List[int]
    test_type: str = "continuity"
    circuit_Num: Optional[int] = None
    PN: Optional[List[int]] = None
    RPO: Optional[List[str]] = None
    note: str = ""

    @classmethod
    def from_yaml(cls, d: dict):
        return cls(
            id=str(d.get("id")),
            source=int(d.get("source")),
            targets=list(d.get("targets", [])),
            test_type=str(d.get("test_type", "continuity")),
            circuit_Num=d.get("circuit_Num"),
            PN=d.get("PN"),
            RPO=d.get("RPO"),
            note=d.get("note", ""),
        )


@dataclass
class TestSummary:
    total: int
    passed: int
    failed: int
    results: List["TestResult"]   # forward reference
