import os

try:
    os.add_dll_directory(os.path.join(os.environ.get("CUDA_PATH_V11_2"), "bin"))
except AttributeError:
    print("cuda not loaded")
import dlc_generic_analysis as dga
from dlc_generic_analysis import gui_utils
from qtpy import QtWidgets, QtCore
import sys
import analysis

try:
    from agati._version import version
except ImportError:
    version = "unknown"


class MainWidget(dga.MainWidget):
    def __init__(self, model_dir: str):
        super().__init__("AGATI")
        self.model_dir = model_dir

    def on_click_analyze(self):
        files = gui_utils.open_files(self, "select videos to analyze")
        if len(files) > 0:
            analysis.analyze(files, model_dir=self.model_dir)

    def on_click_view(self):
        pass

    def on_click_trim(self):
        super(MainWidget, self).on_click_trim()


if __name__ == "__main__":
    name = "agati"
    app = QtWidgets.QApplication.instance()
    if not app:
        if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

        if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        app = QtWidgets.QApplication(sys.argv[1:])
    QtCore.QCoreApplication.setApplicationName(name)
    app.setApplicationName(name)
    app.setApplicationDisplayName(name)
    app.setApplicationVersion(version)
    widget = MainWidget(model_dir=r"C:\Users\la538\git\AGATI\vocal_fold-Nat-2019-08-07")
    window = QtWidgets.QMainWindow()
    window.setCentralWidget(widget)
    window.raise_()
    window.show()
    sys.exit(app.exec_())
