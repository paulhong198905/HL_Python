"""

import random
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



def generate_dummy_test_result(case: WiringHarnessTestCase, force_pass: bool = False) -> TestResult:


    # Simulate measured mask
    measured_mask = 0
    for ch in case.targets:
        measured_mask |= (1 << ch)

    # Fake missing/unexpected
    if force_pass:
        missing_on = []
        unexpected_on = []
    else:
        # Randomly inject an error
        missing_on = random.sample(case.targets, k=random.randint(0, len(case.targets)))
        unexpected_on = random.sample(
            [ch for ch in range(16) if ch not in case.targets],
            k=random.randint(0, 2),
        )

    passed = len(missing_on) == 0 and len(unexpected_on) == 0

    return TestResult(
        test_id=case.id,
        timestamp=datetime.now().isoformat(timespec="seconds"),
        source_channel=case.source,
        expected_targets=case.targets,
        measured_mask=measured_mask,
        missing_on=missing_on,
        unexpected_on=unexpected_on,
        passed=passed,
        circuit_Num=case.circuit_Num,
        PN=case.PN,
        note=case.note,
        error=None if passed else "dummy_failure",
    )


def generate_dummy_summary() -> TestSummary:


    # Fake wiring harness cases (normally from YAML)
    cases = [
        WiringHarnessTestCase(id="CASE001", source=0, targets=[1, 2], circuit_Num=101, PN=[12345]),
        WiringHarnessTestCase(id="CASE002", source=3, targets=[4], circuit_Num=102, PN=[23456]),
        WiringHarnessTestCase(id="CASE003", source=5, targets=[6, 7, 8], circuit_Num=103, PN=[34567]),
    ]

    results = [generate_dummy_test_result(c, force_pass=(i % 2 == 0)) for i, c in enumerate(cases)]
    passed_count = sum(1 for r in results if r.passed)

    return TestSummary(
        total=len(results),
        passed=passed_count,
        failed=len(results) - passed_count,
        results=results,
    )


def print_summary(summary: TestSummary):

    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Total tests: {summary.total}")
    print(f"Passed: {summary.passed}")
    print(f"Failed: {summary.failed}")
    print(f"Success rate: {summary.passed / summary.total * 100:.1f}%")
    print("\nDETAILED RESULTS:")
    print("-" * 50)

    for i, result in enumerate(summary.results, 1):
        print(f"\nTest {i}: {result.test_id}")
        print(f"  Source: {result.source_channel}")
        print(f"  Expected targets: {result.expected_targets}")
        print(f"  Status: {'PASS' if result.passed else 'FAIL'}")
        print(f"  Timestamp: {result.timestamp}")
        if result.missing_on:
            print(f"  Missing connections: {result.missing_on}")
        if result.unexpected_on:
            print(f"  Unexpected connections: {result.unexpected_on}")
        if result.error:
            print(f"  Error: {result.error}")


if __name__ == "__main__":
    summary = generate_dummy_summary()
    print_summary(summary)

"""

import PySide6
print(PySide6.__version__)

