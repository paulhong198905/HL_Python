# /tests/test_UI/demo_UI.py

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, Slot

# 1. The Controller/Emitter (The one that generates the event)
class DataProcessor(QObject):
    """
    This object simulates the MainController or a Worker.
    It processes data and emits a signal when done.
    """
    # Define a Signal: It must be a class attribute.
    # We specify the type of data the signal will carry (str, in this case).

    data_ready = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        print("Processor initialized.")

    def run_processing(self, input_value):
        """Simulates processing a Part Number and getting a result."""
        print(f"Processor: Received input '{input_value}'. Starting work...")

        # Processing logic
        if len(input_value) == 8:
            result = f"Program found for PN: {input_value}."
        else:
            result = "PN too short, please re-scan."

        # 2. Emit the Signal: This instantly triggers all connected Slots.
        self.data_ready.emit(result)





class UIDisplay(QObject):
    """
    This object simulates the MainWindow/View.
    It waits for signals and runs a method (Slot) when one is received.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        print("UI Display initialized.")

    # 4. Define a Slot: This is the method that executes when the signal fires.
    # The @Slot decorator is optional in PySide6, but good practice.
    # The type signature (str) MUST match the Signal's type (Signal(str)).
    @Slot(str)
    def update_display(self, result_message):
        """Updates the simulated UI based on the received message."""
        print("---------------------------------------")
        print(f"UI Display Slot: Signal received!")
        print(f"UI Display Slot: Updating label with: '{result_message}'")
        print("---------------------------------------")







if __name__ == "__main__":
    # QApplication is required even for non-GUI QObject interaction
    app = QApplication(sys.argv)

    # Instantiate the objects
    processor = DataProcessor()
    display = UIDisplay()

    processor.data_ready.connect(display.update_display)
    print("\nConnection established: processor.data_ready --> display.update_display\n")

    # --- Demonstrate Workflow ---

    # Test 1: Invalid PN
    print("--- RUN TEST 1 ---")
    processor.run_processing("12345")

    print("\n--- RUN TEST 2 ---")
    # Test 2: Valid PN (This is where your program name update happens)
    processor.run_processing("87654321")

    # We don't need to run app.exec() since we only demonstrated the immediate function calls.
    sys.exit(0)