import wx
import os
import DataReader
import TrackingObjects
from tracker import Tracker


class Window(wx.Frame):
    """Window object that we'll use as base of GUI"""
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.basicGUI()

    def basicGUI(self):
        menu = wx.MenuBar()
        file_button = wx.Menu()
        exitItem = file_button.Append(wx.ID_EXIT, 'Exit', 'Status msg')
        menu.Append(file_button, 'File')
        self.SetMenuBar(menu)
        self.Bind(wx.EVT_MENU, self.Quit(), exitItem)
        self.SetTitle('VCTrack')
        self.Show(True)


    def Quit(self):
        pass
        # Add more here
        # self.Close()


if __name__ == '__main__':
    app = wx.App()
    window = Window(None)
    # wx.DirDialog() for user friendly directory search
    app.MainLoop()

    # data = DataReader.read_data('vocal1DeepCut_resnet50_vocal_strobeMay8shuffle1_200000.h5')
    # t = Tracker(data)
    # t.frame_by()
    # Gonna do this bit with wx now
