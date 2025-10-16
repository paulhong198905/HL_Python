# presentation/controller/main_controller.py

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Slot

# Type checking import to avoid circular dependencies in imports
if TYPE_CHECKING:
    from business.ckpt.ckpt_model import CkptModel
    from presentation.views.main_window import MainWindow


class MainController(QObject):
    def __init__(self, model: 'CkptModel', view: 'MainWindow'):
        super().__init__()
        self.model = model
        self.view = view

        # Connect Phase 1 signals (PN check status)
        self.model.sig_pn_check_result.connect(self._handle_pn_check_result)

        # Connect Phase 2 signals (Test run status)
        self.model.sig_test_progress.connect(self._handle_test_progress)
        self.model.sig_test_finished.connect(self._handle_test_finished)

        # Connect the dedicated WH test result signal
        self.model.sig_wh_test_result.connect(self.handle_wh_test_result)

        # --- NEW CAN Indicator Connections ---
        # 1. Connect signal for the status indicator lights (Power Mode & Wiper States)
        self.model.sig_indicator_status_update.connect(self._handle_indicator_status_update)

        # 2. Connect signal for the dynamic Wiper Current State text label
        self.model.sig_wiper_current_state_update.connect(self._handle_wiper_current_state_text_update)
        # -------------------------------------

    # --- Slots for UI Input (Phase 1: PN Scan) ---

    @Slot(str)
    def handle_pn_input(self, pn: str):
        """Triggers the model to load the program name if PN is correct length."""
        pn = pn.strip()

        # Check against your required length (e.g., 8 digits)
        if len(pn) == 8:
            print(f"Controller Log: PN length OK. Triggering model lookup for: {pn}")
            self.view.update_test_status(f"Searching for PN: {pn}...", 'black')
            self.model.check_pn_and_get_program_name(pn)
        else:
            # Clear display if input is too short/long
            self.view.update_program_name_display("", 'black')
            self.view.enable_start_button(False)
            self.view.update_test_status("Ready: Enter Part Number (Must be 8 digits)", 'black')

    # --- Slots for Model Output (Phase 1: PN Scan Results) ---

    @Slot(str, str)
    def _handle_pn_check_result(self, message: str, color_flag: str):
        """Handles the result of the quick PN lookup."""

        if color_flag == "fail":
            # PN is bad ("PN NOK" or "PROG NAME MISSING")
            print(f"Controller Log: PN Lookup FAILED. Display: {message}")
            self.view.update_program_name_display(message, 'red')
            self.view.enable_start_button(False)
            self.view.update_test_status(f"Error: {message}", 'red')

        else:  # color_flag == "success"
            program_name = message
            print(f"Controller Log: PN Lookup SUCCESS. Program: {program_name}")
            self.view.update_program_name_display(program_name, 'green')
            self.view.enable_start_button(True)
            self.view.update_test_status(f"Program **{program_name}** loaded. Ready to START.", 'green')

    # --- Slots for UI Input (Phase 2: Start Button Click) ---

    @Slot()
    def start_test_trigger(self):
        """Triggers the model to load full config and start the test sequence."""
        print("Controller Log: Start button clicked. Initiating test sequence.")
        self.view.enable_start_button(False)  # Disable immediately to prevent re-triggering
        self.model.start_test_sequence()

    # --- Slots for Model Output (Phase 2: Test Run Progress & Results) ---

    @Slot(str, int)
    def _handle_test_progress(self, step_name: str, percentage: int):
        """Updates the status bar with current test progress."""
        progress_message = f"TESTING ({percentage}%): {step_name}"
        self.view.update_test_status(progress_message, 'blue')

    @Slot(bool, str)
    def _handle_test_finished(self, success_status: bool, message: str):
        """Handles the final overall result of the test sequence."""
        color = 'green' if success_status else 'red'

        self.view.update_test_status(f"RESULT: {message}", color)

        # Re-enable the start button if the test failed or finished normally
        self.view.enable_start_button(True)
        print(f"Controller Log: Test finished. Success: {success_status}, Message: {message}")

    def handle_wh_test_result(self, result_message: str, color_flag: str):
        """
        Called by the Model when the WH worker finishes.
        Translates the result into a color and updates the View label.
        """
        # Translate Model's flag ('success'/'fail') into a View color string
        if color_flag == 'success':
            color = 'green'
        elif color_flag == 'fail':
            color = 'red'
        elif color_flag == 'bypass':
            color = 'yellow'
        else:
            color = 'gray'  # Should not happen, but safe to include

        # Delegate the actual UI update to the View
        self.view.update_wh_result_label(result_message, color)

    # --- NEW Indicator Status Handlers ---

    @Slot(str, str, bool)
    def _handle_indicator_status_update(self, object_name: str, hit_status_color: str, is_current_active: bool):
        """
        Handles updates for Power Mode and Wiper state indicators.
        The Model provides the 'permanent' color (yellow/green) and whether the state is currently active.
        """
        print(
            f"Controller Log: Indicator update for {object_name}: Color={hit_status_color}, Active={is_current_active}")

        # The View needs a dedicated method to handle the complex state (Color + Active state)
        self.view.update_indicator_status(object_name, hit_status_color, is_current_active)

    @Slot(str)
    def _handle_wiper_current_state_text_update(self, state_text: str):
        """
        Updates the lbl_Wiper_CurrentState label text and background color.

        Logic: Background Green if state is 'OFF', Yellow otherwise.
        """
        upper_state = state_text.upper()
        display_text = f"WIPER: {state_text}"

        # Determine the background color
        if upper_state == 'OFF':
            # Background Green when Wiper state is OFF
            bg_color = 'green'
            text_color = 'white'
        else:
            # Background Yellow for any other Wiper state (Intermittent, Slow/Low, etc.)
            bg_color = 'yellow'
            text_color = 'black'

        # Call the View method, which now accepts the background color argument
        self.view.update_label_text("lbl_Wiper_CurrentState", display_text, text_color, bg_color)