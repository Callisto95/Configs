import sys

from PySide6.QtWidgets import QApplication

from python_scripts.quickbac.crop import HorizontalCropper, VerticalCropper
from python_scripts.quickbac.data import ImageProcessorFactory
from python_scripts.quickbac.fill import HorizontalFiller, VerticalFiller
from python_scripts.quickbac.ui import QuickBackUI

app: QApplication = QApplication(sys.argv)


decider: ImageProcessorFactory = ImageProcessorFactory()

decider.register(True, False, HorizontalFiller())
decider.register(True, True, HorizontalCropper())
decider.register(False, False, VerticalFiller())
decider.register(False, True, VerticalCropper())

ui: QuickBackUI = QuickBackUI(decider)

ui.show()
sys.exit(app.exec())
