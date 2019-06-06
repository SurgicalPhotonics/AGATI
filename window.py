import wx
import os
import DataReader
import TrackingObjects
from Tracker import Tracker
from tkinter import Tk
from tkinter.filedialog import askopenfilename


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


if __name__ == '__main__':
    app = wx.App()
    window = Window(None)
    # wx.DirDialog() for user friendly directory search
    dlg = wx.MessageBox('Would you like to analyze a new video?', 'Confirm',
                        wx.YES_NO)
    path = window.file_select()
    app.MainLoop()

    # data = DataReader.read_data('vocal1DeepCut_resnet50_vocal_strobeMay8shuffle1_200000.h5')
    # t = Tracker(data)
    # t.frame_by()
    # Gonna do this bit with wx now
