# business/ckpt/ckpt_model.py

import time
from typing import Dict, Any, Tuple
import threading
import logging
from PySide6.QtCore import QObject, Signal, QThread

from business.ckpt.config_manager import ConfigManager, ConfigurationError
from business.workers.wh_test_worker import WhTestWorker
from business.workers.can_state_store import CanStateStore
from business.workers.can_test_worker import CanTestWorker
from can_fd.canfd.canfd_enum import CANDLC
from hardware.can.PCANBasic import PCANBasic, TPCANMsgFD
from hardware.can.pcan_constants import PCANCh, bitrate_fd_500K_2Mb, PCAN_ALLOW_ECHO_FRAMES, PCAN_PARAMETER_ON, \
    PCAN_ERROR_OK, PCAN_MESSAGE_EXTENDED, PCAN_MESSAGE_FD, PCAN_MESSAGE_STANDARD, PCAN_MESSAGE_BRS

logger = logging.getLogger(__name__)


class CkptModel(QObject):
    # Phase 1 Signal: Program Name Check Result
    sig_pn_check_result = Signal(str, str)  # (message, color_flag: 'success' or 'fail')

    # Phase 2 Signals: Worker progress (relayed to Controller/UI)
    sig_test_progress = Signal(str, int)
    sig_test_finished = Signal(bool, str)

    # Dedicated signal for the Wiring Harness Test final result
    sig_wh_test_result = Signal(str, str)  # (result_message, color_flag)

    # Dedicated signal for Power Mode update (useful for the UI)
    sig_power_mode_update = Signal(str)

    # UPDATED: Signal now carries the color string ('yellow' or 'green')
    # Args: (object_name, hit_status_color: 'yellow'/'green', is_current_active: bool)
    sig_indicator_status_update = Signal(str, str, bool)

    # Signal to update the lbl_Wiper_CurrentState label text (only text update needed)
    sig_wiper_current_state_update = Signal(str)

    BYPASS_WH_TEST: bool = True

    # Map raw signal states to UI object names (for the indicator logic)
    STATE_TO_OBJECT_NAME = {
        # Power Mode States
        "OFF": "lbl_PowerMode_Off",
        "RUN": "lbl_PowerMode_Run",
        # Wiper States (Based on Windshield_Wiper_Switch_Status value)
        "OFF": "lbl_Wiper_Off",
        "INTERMITTENT": "lbl_Wiper_Intermittent",
        "SLOW": "lbl_Wiper_Slow",
    }

    # Wiper Signal Name
    WIPER_SIGNAL_NAME = "Windshield_Wiper_Switch_Status"

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.current_pn_config: Dict[str, Any] = {}
        self.worker_input_map: Dict[str, str] = {}
        self.active_workers: Dict[str, QThread] = {}
        self.test_statuses: Dict[str, Any] = {}

        # --- PCAN Ownership & CAN TX Thread Management ---
        self.pcan = None
        self.channel = PCANCh.default
        self.sequence_stop_event = threading.Event()
        self.t_wakeup = None
        self.t_tester_present = None
        # -------------------------------------------------

        self.can_state_store = CanStateStore()

        # Tracking dictionary for the "Never Hit = Yellow, Once Hit = Green" logic
        self.indicator_hit_status: Dict[str, bool] = {
            "lbl_PowerMode_Off": False,
            "lbl_PowerMode_Run": False,
            "lbl_Wiper_Off": False,
            "lbl_Wiper_Intermittent": False,
            "lbl_Wiper_Slow": False,
        }

        # Connect the state store to the model's signal for UI/logic updates
        self.can_state_store.sig_power_mode_changed.connect(self._handle_pm_state_change)
        self.can_state_store.sig_signal_updated.connect(self._handle_generic_signal_update)

    def _initialize_pcan(self) -> bool:
        """Initializes PCANBasic and stores the object."""
        if self.pcan:
            return True

        try:
            self.pcan = PCANBasic()
            self.pcan.InitializeFD(self.channel, bitrate_fd_500K_2Mb)
            self.pcan.SetValue(self.channel, PCAN_ALLOW_ECHO_FRAMES, PCAN_PARAMETER_ON)
            time.sleep(0.5)
            print("CKPT Model: PCAN Hardware initialized successfully.")
            return True
        except Exception as e:
            print(f"ERROR: PCAN Initialization failed: {e}")
            self.pcan = None
            return False

    def _cleanup_can_tx_threads(self):
        """Stops and joins the periodic TX threads."""
        if self.sequence_stop_event.is_set():
            return

        print("CKPT Model: Stopping periodic CAN TX threads.")
        self.sequence_stop_event.set()

        if self.t_wakeup and self.t_wakeup.is_alive():
            self.t_wakeup.join(0.5)

        if self.t_tester_present and self.t_tester_present.is_alive():
            self.t_tester_present.join(0.5)

        self.sequence_stop_event.clear()
        self.t_wakeup = None
        self.t_tester_present = None

    def _uninitialize_pcan(self):
        """Cleans up the PCAN hardware, including stopping TX threads."""
        self._cleanup_can_tx_threads()

        if self.pcan:
            print("CKPT Model: Uninitializing PCAN hardware.")
            self.pcan.Uninitialize(self.channel)
            self.pcan = None

    def _write_can_message(self, msg: TPCANMsgFD):
        """Internal helper to write the message and log the result."""
        result = self.pcan.WriteFD(self.channel, msg)

        if result == PCAN_ERROR_OK:
            try:
                logger.info(
                    f"TX: ID=0x{msg.ID:X}, DLC={msg.DLC}; Data: {[msg.DATA[i] for i in range(msg.DLC)]}"
                )
            except NameError:
                print(f"TX: ID=0x{msg.ID:X} sent OK. Data: {[msg.DATA[i] for i in range(msg.DLC)]}")
        else:
            try:
                logger.error(f"TX FAILED: ID=0x{msg.ID:X}. Error: {self.pcan.GetErrorText(result)}")
            except NameError:
                print(f"TX FAILED: ID=0x{msg.ID:X}. Error: {self.pcan.GetErrorText(result)}")

    def _periodic_tx_thread(self, pcan: PCANBasic, channel,
                            stop_event: threading.Event,
                            msg: TPCANMsgFD,
                            interval: float = 0.5):
        """
        Periodically transmit a CAN/CAN FD message until stop_event is set.
        """
        logger.info(f"Periodic TX thread started for ID=0x{msg.ID:X}, DLC={msg.DLC}, every {interval}s")

        while not stop_event.is_set():
            result = pcan.WriteFD(channel, msg)

            if result == PCAN_ERROR_OK:
                logger.debug(
                    f"TX: ID=0x{msg.ID:X}, DLC={msg.DLC}; Data: {[msg.DATA[i] for i in range(msg.DLC)]}"
                )
            else:
                logger.error(f"Periodic TX failed for ID 0x{msg.ID:X}: {pcan.GetErrorText(result)}")

            time.sleep(interval)

        logger.info(f"Periodic TX thread for ID 0x{msg.ID:X} stopped.")

    def _send_initial_can_command(self):
        """
        Executes the complex, timed CAN/UDS sequence, including starting periodic threads.
        """
        if not self.pcan:
            print("ERROR: PCAN not initialized. Cannot send command.")
            return

        # --- Periodic Wakeup Thread (0x638) ---
        msg_wakeup = TPCANMsgFD()
        msg_wakeup.ID = 0x638
        msg_wakeup.MSGTYPE = PCAN_MESSAGE_STANDARD
        msg_wakeup.DLC = 8
        msg_wakeup.DATA[0:8] = (0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        self.t_wakeup = threading.Thread(
            target=self._periodic_tx_thread,
            args=(self.pcan, self.channel, self.sequence_stop_event, msg_wakeup, 0.6),
            daemon=True,
        )
        self.t_wakeup.start()
        print("Started periodic 0x638 (Wakeup) @ 500ms.")

        time.sleep(0.5)

        # --- Periodic Tester Present Thread (0x14DA40F1) ---
        msg_tp = TPCANMsgFD()
        msg_tp.ID = 0x14DA40F1
        msg_tp.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg_tp.DLC = 8
        msg_tp.DATA[0:8] = (0x02, 0x3E, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00)
        self.t_tester_present = threading.Thread(
            target=self._periodic_tx_thread,
            args=(self.pcan, self.channel, self.sequence_stop_event, msg_tp, 2.0),
            daemon=True,
        )
        self.t_tester_present.start()
        print("Started periodic 0x14DA40F1 (Tester Present) @ 1000ms.")

        time.sleep(0.5)

        # --- One-Time UDS Commands ---
        msg_1003 = TPCANMsgFD()
        msg_1003.ID = 0x14DA40F1
        msg_1003.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg_1003.DLC = CANDLC.DLC_8H_8B
        msg_1003.DATA[0:8] = (0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00)
        self._write_can_message(msg_1003)
        time.sleep(1.5)

        msg_2701 = TPCANMsgFD()
        msg_2701.ID = 0x14DA40F1
        msg_2701.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg_2701.DLC = CANDLC.DLC_8H_8B
        msg_2701.DATA[0:8] = (0x02, 0x27, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00)
        self._write_can_message(msg_2701)
        time.sleep(0.5)

        msg_2702 = TPCANMsgFD()
        msg_2702.ID = 0x14DA40F1
        msg_2702.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg_2702.DLC = CANDLC.DLC_AH_16B
        msg_2702.DATA[0:16] = (
            0x00, 0x0E, 0x27, 0x02, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x11, 0x12)
        self._write_can_message(msg_2702)
        time.sleep(1.5)

        msg_iocontrol = TPCANMsgFD()
        msg_iocontrol.ID = 0x14DA40F1
        msg_iocontrol.MSGTYPE = PCAN_MESSAGE_EXTENDED | PCAN_MESSAGE_FD | PCAN_MESSAGE_BRS
        msg_iocontrol.DLC = CANDLC.DLC_8H_8B
        msg_iocontrol.DATA[0:8] = (0x07, 0x2F, 0xFD, 0x04, 0x03, 0x80, 0x00, 0x03)
        self._write_can_message(msg_iocontrol)

        print("UDS command sequence (main thread) completed.")

    def _update_indicators(self, signal_states: Dict[str, str], active_state_name: str, active_state_signal: str):
        """
        Handles the core logic for indicator state updates (hit status and current active status).
        UPDATED: Calculates and emits the color string ('yellow' or 'green').
        Args:
            signal_states: Map of UI object names to their corresponding signal values.
            active_state_name: The current value of the signal (e.g., 'OFF', 'RUN').
            active_state_signal: The name of the signal being processed (e.g., 'PowerMode', 'Wiper').
        """
        for state_name, object_name in signal_states.items():

            is_hit = self.indicator_hit_status.get(object_name, False)
            is_current_active = (state_name == active_state_name)

            # 1. Update hit status (Once hit, always hit)
            if is_current_active and not is_hit:
                self.indicator_hit_status[object_name] = True
                is_hit = True

            # 2. Determine the color based on your logic:
            # - If currently active: MUST be green (and bright/solid in the UI Controller).
            # - If not active, but was hit: GREEN (stays green, but dim/off in the UI Controller).
            # - If not active, and NEVER hit: YELLOW.
            if is_hit:
                hit_status_color = 'green'
            else:
                hit_status_color = 'yellow'

            # 3. Emit the update for the UI Controller
            # The UI Controller should use (hit_status_color AND is_current_active) to draw the final appearance.
            self.sig_indicator_status_update.emit(object_name, hit_status_color, is_current_active)

    def _handle_generic_signal_update(self, signal_name: str, new_value: Any):
        """Checks for non-critical signal updates, like Wiper Status."""
        if signal_name == self.WIPER_SIGNAL_NAME:
            print(f" CKPT Model (MAIN THREAD): Received Wiper Update: {new_value}")

            # 1. Update the indicator lights (lbl_Wiper_Off, etc.)
            wiper_states_map = {
                "OFF": "lbl_Wiper_Off",
                "INTERMITTENT": "lbl_Wiper_Intermittent",
                "SLOW": "lbl_Wiper_Slow",
                # FIX 1: Map the 'LOW' decoded status to the 'Slow' indicator label
                "LOW": "lbl_Wiper_Slow",
            }

            # Use the new_value (which might be 'LOW')
            current_state_key = str(new_value).upper()

            # Filter the states we are tracking for the hit logic
            filtered_wiper_states = {k: v for k, v in wiper_states_map.items() if v in self.indicator_hit_status}

            # Update indicators and emit sig_indicator_status_update
            self._update_indicators(filtered_wiper_states, current_state_key, 'WIPER')

            # 2. Update the dedicated text label (lbl_Wiper_CurrentState)
            self.sig_wiper_current_state_update.emit(str(new_value))

    def _handle_pm_state_change(self, new_state: str):
        """Relays the Power Mode state change and updates indicators."""
        print(f" CKPT Model (MAIN THREAD): Received PowerMode update: '{new_state}'")

        # Relay to Controller for UI update or logic checks (generic update)
        self.sig_power_mode_update.emit(new_state)

        # --- Power Mode Indicator Logic ---
        pm_states_map = {
            "OFF": "lbl_PowerMode_Off",
            "RUN": "lbl_PowerMode_Run",
        }
        # Only update for the states we are tracking for the hit logic
        filtered_pm_states = {k: v for k, v in pm_states_map.items() if v in self.indicator_hit_status}

        # Update indicators and emit sig_indicator_status_update
        self._update_indicators(filtered_pm_states, new_state, 'POWER_MODE')

    def check_pn_and_get_program_name(self, pn: str) -> None:
        """PHASE 1: Quick check of PN against the map and displays status."""
        print(f"CKPT Model: PHASE 1 - Checking PN: {pn}")

        try:
            program_name = self.config_manager.get_program_name(pn)

            if program_name == 'UNKNOWN_PROGRAM_KEY_MISSING':
                self.current_pn_config = {}
                print("CKPT Model Error: Program Name key missing in map entry.")
                self.sig_pn_check_result.emit("PROG NAME MISSING", 'fail')
                return

            self.current_pn_config = {'pn': pn}
            print(f"CKPT Model: Quick check SUCCESS for Program: {program_name}")
            self.sig_pn_check_result.emit(program_name, 'success')

        except ConfigurationError as e:
            self.current_pn_config = {}
            print(f"CKPT Model: Configuration Load Error: {e}")
            self.sig_pn_check_result.emit("PN NOK", 'fail')

    def _prepare_worker_inputs(self, filenames_map: Dict[str, Any]) -> Dict[str, str]:
        """Creates the mapping from worker ID to its required configuration file path."""
        worker_map = {}

        KEY_TO_WORKER_ID = {
            'wh_config_file': 'HARDWARE_TEST',
            'diag_config_file': 'DIAGNOSTIC_TEST',
            'can_decode_file': 'CAN_DECODE_TEST',
        }

        for file_key, worker_id in KEY_TO_WORKER_ID.items():
            filename = filenames_map.get(file_key)
            if filename:
                worker_map[worker_id] = f"config/{filename}"

        return worker_map

    def _handle_worker_progress(self, message: str, percentage: int, worker_id: str):
        """Relay progress from any worker to the main status bar (sig_test_progress)."""
        self.sig_test_progress.emit(f"[{worker_id}] {message}", percentage)

    def _handle_worker_finished(self, success: bool, result_msg: str, worker_id: str):
        """Handle the final result from a worker thread."""
        print(f"Worker {worker_id} finished. Success: {success}. Msg: {result_msg}")

        color_flag = 'success' if success else 'fail'
        self.sig_wh_test_result.emit(result_msg, color_flag)

        if worker_id in self.active_workers:
            self.active_workers[worker_id].quit()
            self.active_workers[worker_id].wait(100)
            del self.active_workers[worker_id]

        if not self.active_workers:
            print("CKPT Model: All workers completed.")
            # Final hardware cleanup, including stopping TX threads
            self._uninitialize_pcan()

    def start_test_sequence(self):
        """PHASE 2: Gathers config file paths and prepares to launch parallel workers."""
        pn = self.current_pn_config.get('pn')
        if not pn:
            self.sig_test_finished.emit(False, "Error: No valid PN loaded. Scan PN first.")
            return

        if self.active_workers:
            print("CKPT Model: Test already running. Ignoring start request.")
            return

        print(f"CKPT Model: PHASE 2 - Gathering config file paths for PN: {pn}")
        self.sig_test_progress.emit("Mapping configuration files to test modules...", 5)

        if not self._initialize_pcan():
            self.sig_test_finished.emit(False, "CAN Hardware Initialization Failed.")
            return

        try:
            filenames_map = self.config_manager.get_pn_config_filenames(pn)
            self.worker_input_map = self._prepare_worker_inputs(filenames_map)

            self.current_pn_config.update({
                'program_name': filenames_map.get('program_name'),
                'description': filenames_map.get('description', 'No Description')
            })

            self.sig_test_progress.emit("Worker inputs prepared. Initializing Parallel Tests...", 10)
            time.sleep(0.5)

            print(
                f"CKPT Model: SUCCESSFULLY MAPPED {len(self.worker_input_map)} TEST MODULES. STARTING PARALLEL THREAD CREATION.")
            print("CKPT Model: Worker Input Map Content:")

            # 3. Launch the Parallel Workers
            for worker_id, file_path in self.worker_input_map.items():
                print(f"  - {worker_id:<20}: {file_path}")

                if worker_id == 'HARDWARE_TEST':
                    if not self.BYPASS_WH_TEST:
                        print("TODO: wh continuity test")
                        worker = WhTestWorker(config_filepath=file_path, worker_id=worker_id)
                        worker.sig_test_finished.connect(self._handle_worker_finished)
                        worker.sig_progress_updated.connect(self._handle_worker_progress)
                        self.active_workers[worker_id] = worker
                        worker.start()
                        print(f"CKPT Model: Started WH Test Worker ID: {worker_id}")
                    if self.BYPASS_WH_TEST:
                        print("BYPASS WH continuity test. Not starting worker.")
                        self.sig_wh_test_result.emit("bypassed wh tests", 'bypass')
                        continue

                if worker_id == 'CAN_DECODE_TEST':
                    decoder_cfg = file_path
                    validation_file_key = 'can_validation_file'
                    validation_cfg = self.worker_input_map.get(
                        validation_file_key,
                        "config/PN36666666_can_validation.yaml"
                    )

                    worker = CanTestWorker(
                        pcan_instance=self.pcan,
                        can_state_store=self.can_state_store,
                        decoder_cfg=decoder_cfg,
                        validation_cfg=validation_cfg,
                        parent=self
                    )

                    worker.sig_test_finished.connect(lambda s, m: self._handle_worker_finished(s, m, worker_id))
                    worker.sig_progress_updated.connect(lambda m, p: self._handle_worker_progress(m, p, worker_id))

                    self.active_workers[worker_id] = worker
                    worker.start()
                    print(f"CKPT Model: Started CAN Monitoring/Decoding Worker ID: {worker_id}")

                    # Stop here to focus on CAN monitoring before running other tests
                    break

            # --- EXECUTE HARD-CODED COMMAND HERE ---
            self._send_initial_can_command()
            # ---------------------------------------

        except ConfigurationError as e:
            error_message = f"Error during Phase 2 loading: {e}"
            print(f"CKPT Model Error: {error_message} (PN: {pn})")
            self.sig_test_finished.emit(False, error_message)
            self.sig_test_progress.emit("Configuration Load Failed.", 100)
            self._uninitialize_pcan()