import wx
import os
import DataReader
import matplotlib.pyplot as plt
from tracker import Tracker
from tkinter import*
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import dlc_script as scr
# Put dlc project inside app install folder


class Window(wx.Frame):
    """Window object that we'll use as base of GUI"""
    def __init__(self):
        wx.Frame.__init__(self, None, title='VCTrack')
        panel = wx.Panel(self)

        lbl = wx.StaticText(panel, -1, style=wx.ALIGN_CENTER)
        font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        lbl.SetFont(font)
        closebtn = wx.Button(panel, label='Close')
        closebtn.Bind(wx.EVT_BUTTON, self.quit)

    def quit(self, event):
        self.Close()

    def file_select(self):
        """Prompts user to select input file for analysis."""
        dlg = wx.MessageBox('Would you like to analyze a new video?', 'Confirm',
                            wx.YES_NO)
        if dlg == wx.YES:
            Tk().withdraw()
            return askopenfilename()
        else:
            dlg = wx.MessageBox('Would you like to close the program?', 'Confirm',
                                wx.YES_NO)
            if dlg == wx.YES:
                self.quit()
            else:
                self.file_select()


def run():
    name = os.path.dirname(os.path.abspath(__file__))
    cfg = name + '\\vocal-Nat-2019-06-10'
    app = wx.App(False)
    window = Window()
    window.Show()
    path = window.file_select()
    scr.new_vid(cfg, path)
    data_path = scr.analyze(cfg, path)
    scr.new_vid(cfg, path)
    vid_path = scr.label(cfg, path)
    data = DataReader.read_data(data_path)
    T = Tracker(data)
    d_list = T.frame_by(vid_path)
    app.MainLoop()
    plt.show()


if __name__ == '__main__':
    run()

