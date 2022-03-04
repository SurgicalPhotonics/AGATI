import os.path
os.environ["QT_API"] = "pyside2"
import sys
import numpy as np
import pandas as pd
import dlc_generic_analysis as dga
from qtpy import QtCore, QtWidgets, QtMultimedia
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure


class ViewWidget(dga.ViewerWidget):
    def __init__(self, path):
        """
        displays a video alog size a plots of the anterior glottic angle, false vocal fold angle
        width of vocal folds and angle between vocal fold and aeryepiglottis
        """
        super(ViewWidget, self).__init__()
        self.canvas = FigureCanvas(Figure())
        sp_plots = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sp_plots.setHorizontalStretch(1.5)
        self.canvas.setSizePolicy(sp_plots)
        sp_video = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sp_video.setHorizontalStretch(1)
        self.video_viewer.setSizePolicy(sp_video)
        self.content_layout.addWidget(self.canvas)
        self.load_video(path)

    def position_changed(self, position) -> None:
        super(ViewWidget, self).position_changed(position)

    def load_video(self, path: str, filetype=".h5") -> None:
        if filetype == "h5" or filetype == ".h5":
            data_path = os.path.splitext(path)[0] + ".h5"
            data = pd.read_hdf(data_path)
            data = data[os.path.split(os.path.splitext(path)[0])[1]]
            xs = np.arange(data["true", "angles"].to_numpy().shape[0])
            axs = self.canvas.figure.subplots(2, 2, sharex=True)
            self.canvas.figure.tight_layout()

            # true
            axs[0, 0].plot(xs, data["true", "angles"].to_numpy())
            axs[0, 0].plot(xs, data["true", "angles_l"].to_numpy())
            axs[0, 0].plot(xs, data["true", "angles_r"].to_numpy())
            axs[0, 0].set_title("Anterior Glottic Angle (º)")

            # false
            axs[1, 0].plot(xs, data["false", "angles"].to_numpy())
            axs[1, 0].plot(xs, data["true", "angles_l"].to_numpy())
            axs[1, 0].plot(xs, data["true", "angles_r"].to_numpy())
            axs[1, 0].set_title("False Vocal Cord Angle (º)")

            # widths
            axs[0, 1].set_title("vocal cord width (px)")
            axs[0, 1].plot(xs, data["cord_widths", "l"].to_numpy())
            axs[0, 1].plot(xs, data["cord_widths", "r"].to_numpy())

            # AEG_trues
            axs[1, 1].set_title("Aryepiglottis true vocal cord angle (º)")
            axs[1, 1].plot(xs, data["aeg_true", "angle_l"].to_numpy())
            axs[1, 1].plot(xs, data["aeg_true", "angle_r"].to_numpy())

            # self.canvas.figure.subplots_adjust(wspace=.1)
            self._video_player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path)))
            super(ViewWidget, self).load_video(path)
            self._video_player.play()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    viewer = ViewWidget(r"C:\Users\la538\Desktop\AGATI validation\2_analyzed.mp4")
    viewer.show()
    app.exec_()
