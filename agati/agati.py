from qtpy import QtWidgets, QtCore, QtGui
import sys

if not QtWidgets.QApplication.instance():
    if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
else:
    app = QtWidgets.QApplication.instance()
splash_img = QtGui.QPixmap("../splashscreen.jpg")
screen = QtGui.QGuiApplication.primaryScreen().availableGeometry()
wd_fix = (int(screen.width() / 3), int(screen.width() / 3 * 0.795333333))
ht_fix = (int(screen.height() / 3 * 1.25733445), int(screen.height() / 3))
if wd_fix[0] > ht_fix[0]:
    splash_img = splash_img.scaled(wd_fix[0], wd_fix[1])
else:
    splash_img = splash_img.scaled(ht_fix[0], ht_fix[1])
splash = QtWidgets.QSplashScreen(splash_img)
splash.show()
# add cuda dll directory path
import os

if sys.platform == "win32":
    try:
        os.add_dll_directory(os.path.join(os.environ.get("CUDA_PATH_V11_2"), "bin"))
    except AttributeError:
        try:
            os.add_dll_directory(os.path.join(os.environ.get("CUDA_PATH"), "bin"))
        except AttributeError:
            print("cuda not loaded")
import dlc_generic_analysis as dga
from dlc_generic_analysis import gui_utils
import analysis
import tensorflow as tf
from viewer import ViewWidget

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
            analysis.analyze(self.model_dir, files)
            print("Done.")

    def on_click_view(self):
        video_paths = dga.gui_utils.open_files(self, "Analyzed video")
        if len(video_paths) > 0:
            viewer = ViewWidget(video_paths[0])
            viewer.show()

    def on_click_trim(self):
        super(MainWidget, self).on_click_trim()


if __name__ == "__main__":
    print(f"Found {len(tf.config.list_physical_devices('GPU'))} GPUs")
    print(f"Found {len(tf.config.list_logical_devices('TPU'))} TPUs")
    name = "agati"
    app.setApplicationName(name)
    app.setApplicationDisplayName(name)
    app.setApplicationVersion(version)
    widget = MainWidget(model_dir="AGATIv2-Matt-2020-06-10")
    window = QtWidgets.QMainWindow()
    window.setCentralWidget(widget)
    window.raise_()
    window.show()
    splash.finish(window)
    sys.exit(app.exec_())
