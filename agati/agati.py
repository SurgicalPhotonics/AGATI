import dlc_generic_analysis as dga
from dlc_generic_analysis import gui_utils
from agati import analyze


class MainWindow(dga.MainWidget):
    def __init__(self):
        super().__init__("AGATI")

    def on_click_analyze(self):
        files = gui_utils.open_files(self, "select videos to analyze")
        if len(files) > 0:
            analysis.analyze()

    def on_click_view(self):
        pass

    def on_click_trim(self):
        super(MainWindow, self).on_click_trim()


