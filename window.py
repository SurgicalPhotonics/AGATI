import wx
import os
import sys
import DataReader
import TrackingObjects
from Tracker import Tracker
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import dlc_script as scr
# Put dlc project inside app install folder

class Window(wx.Frame):
    """Window object that we'll use as base of GUI"""
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.basicGUI()

    def basicGUI(self):
        """Basic GUI operations."""
        menu = wx.MenuBar()
        file_button = wx.Menu()
        exitItem = file_button.Append(wx.ID_EXIT, 'Exit', 'Status msg')
        menu.Append(file_button, 'File')
        self.SetMenuBar(menu)
        self.Bind(wx.EVT_MENU, self.quit(), exitItem)
        self.SetTitle('VCTrack')
        self.Show(True)

    def quit(self):
        # Add more here
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
    cfg = os.path.join(sys.argv[0], '\\vp-Nat-2019-06-05')
    app = wx.App()
    window = Window(None)
    # wx.DirDialog() for user friendly directory search
    dlg = wx.MessageBox('Would you like to analyze a new video?', 'Confirm',
                        wx.YES_NO)
    path = window.file_select()
    scr.new_vid(cfg, path)
    data_path = scr.analyze(cfg, path)
    vid_path = scr.new_vid(cfg, path)
    data = DataReader.read_data(data_path)
    T = Tracker(data)
    T.frame_by(vid_path)
    app.MainLoop()


if __name__ == '__main__':
    run()
