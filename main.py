# tests/test_UI/main_UI.py
import sys
from PySide6.QtWidgets import QApplication

from business.ckpt.ckpt_model import CkptModel
from presentation.controller.main_controller import MainController
from presentation.views.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 1. Instantiate the Model (CKPT specific)
    model = CkptModel()

    # 2. Instantiate the View FIRST, injecting the Controller dependency
    # The View needs the Controller to set up its initial connections in __init__.
    # NOTE: Since the Controller requires the View, we often pass the Controller
    # to the View *after* the Controller is created, which leads to a temporary
    # cycle problem. The cleanest way to handle this is to use a setter on the Controller.

    # 2a. Instantiate the View (pass None for controller initially, or rely on internal View structure)
    # The standard approach is to pass the Controller to the View:
    view = MainWindow(controller=None)

    # 3. Instantiate the Controller, injecting the Model and the View
    # Fix: Now we pass both 'model' and 'view'
    controller = MainController(model=model, view=view)

    # 4. Final step to break the cycle: Inject the *fully initialized* controller back into the view.
    # We must assume you have a 'set_controller' method in MainWindow, or update MainWindow's __init__
    # to handle the deferred assignment. Assuming a dedicated method for now:
    view.set_controller(controller)

    # 5. The PN input connection should be inside the View's _connect_ui method.
    # The line 'view.pn_input_changed.connect(controller.check_program_trigger)' remains unnecessary here.

    view.show()
    sys.exit(app.exec())