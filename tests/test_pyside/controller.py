# tests/test_pyside/controller.py
from model import DataModel
from PySide6.QtWidgets import QWidget  # Placeholder for type hinting


class TestController:
    """
    The Controller: Manages the Data Model and updates the View.
    """

    def __init__(self, view_instance: QWidget):
        self.view = view_instance
        self.model = DataModel()

        # Connect the Model's signal directly to the View's update slot
        # The View's slot will be executed safely in the UI thread.
        self.model.status_update.connect(self.update_view_from_model)

    def start_test(self):
        """Starts the data generation thread."""
        print("Controller: Starting data thread...")
        self.model.start()

    def stop_test(self):
        """Stops the data generation thread."""
        print("Controller: Stopping data thread...")
        self.model.stop()

    def update_view_from_model(self, data: dict):
        """
        Slot connected to the DataModel's signal.
        This method executes in the safe main UI thread.
        """
        # In a real app, you would translate raw data into test status here

        # Example: Determine a simple PASS/FAIL status
        rpm_status = "PASS" if data["EngineRPM"] < 2000 else "HIGH RPM (FAIL)"

        # Send the final, processed status to the View to update labels
        self.view.update_status(data, rpm_status)

    # In a full application, methods like start_uds_session() would go here
    # to receive commands from the View and execute them in the Model/Engine.