from qtpy import QtWidgets, QtCore, QtGui
import sys
app = QtWidgets.QApplication(sys.argv[1:])
splash_img = QtGui.QPixmap("../splashscreen.jpg")
screen = app.desktop().screenGeometry()
wd_fix = (int(screen.width()/3), int(screen.width()/3*0.795333333))
ht_fix = (int(screen.height()/3*1.25733445), int(screen.height()/3))
if wd_fix[0] > ht_fix[0]:
    splash_img = splash_img.scaled(wd_fix[0], wd_fix[1])
else:
    splash_img = splash_img.scaled(ht_fix[0], ht_fix[1])
splash = QtWidgets.QSplashScreen(splash_img)
splash.show()

import os
try:
    os.add_dll_directory(os.path.join(os.environ.get("CUDA_PATH_V11_2"), "bin"))
except AttributeError:
    print("cuda not loaded")
import dlc_generic_analysis as dga
from dlc_generic_analysis import gui_utils
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
        print("Done.")

    def on_click_view(self):
        pass

    def on_click_trim(self):
        super(MainWidget, self).on_click_trim()


if __name__ == "__main__":
    name = "agati"
    QtCore.QCoreApplication.setApplicationName(name)
    app.setApplicationName(name)
    app.setApplicationDisplayName(name)
    app.setApplicationVersion(version)
    widget = MainWidget(model_dir=r"C:\Users\la538\git\AGATI\vocal_fold-Nat-2019-08-07")
    window = QtWidgets.QMainWindow()
    window.setCentralWidget(widget)
    window.raise_()
    splash.finish(window)
    window.show()
    sys.exit(app.exec_())
