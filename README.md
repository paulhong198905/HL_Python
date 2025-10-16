CKPT CAN & Harness Test Station

Overview:
1. The CKPT CAN & Harness Test Station is a specialized desktop application built with Python and PySide6 (Qt) designed for automotive component verification. It implements a Model-View-Controller (MVC) architecture to ensure proper Part Number (PN) configuration, validate wiring harness continuity, and monitor/validate critical CAN Bus signals in real-time.

Key Capabilities:
1. Part Number (PN) Management: Loads configuration profiles based on the scanned PN.
2. Wiring Harness (WH) Continuity Check: Executes hardware tests (simulated or real) with clear pass/fail results.
3. Real-time CAN Monitoring: Decodes signals like Vehicle Power Mode and Wiper Switch Status.
4. State Verification: Uses visual indicators (Green/Yellow) to track if critical component states (e.g., Ignition ON/OFF, Wiper speeds) have been successfully achieved during the test sequence.

Prerequisites:
	Hardware Requirements:
		1. CAN Interface: A compatible PCAN-FD device (e.g., PEAK-System PCAN-USB Pro FD).
		2. Test Fixture: Custom hardware/wiring harness fixture for continuity testing.
		3. Vehicle Interface: Connection to the Electronic Control Unit (ECU) under test.
	Software Requirements:
		1. Python: Version 3.8 or higher.
		2. Operating System: [Specify OS: e.g., Windows 10/11].
