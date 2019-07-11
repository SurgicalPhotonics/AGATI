import wx
import os
import DataReader
import yaml
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

        self.lbl = wx.StaticText(panel, -1, style=wx.ALIGN_LEFT)
        font = wx.Font(12, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        self.lbl.SetFont(font)
        self.lbl2 = wx.StaticText(panel, -1, style=wx.ALIGN_LEFT, pos=(0, 20))
        self.lbl2.SetFont(font)
        self.lbl3 = wx.StaticText(panel, -1, style=wx.ALIGN_LEFT, pos=(0, 40))
        self.lbl3.SetFont(font)
        self.lbl4 = wx.StaticText(panel, -1, style=wx.ALIGN_LEFT, pos=(0, 60))
        self.lbl4.SetFont(font)

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
    cfg = os.path.join(name, 'vocal-Nat-2019-06-10')
    file_name = os.path.join(cfg, 'config.yaml')
    stream = open(file_name, 'r')
    data = yaml.load(stream)
    data['project_path'] = cfg
    with open(file_name, 'w') as yaml_file:
        yaml_file.write(yaml.dump(data, default_flow_style=False))
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
    window.lbl.SetLabel('Your video with printed lines can be found here: ' +
                        d_list[0])
    min = str(round(float(d_list[1]), 2))
    window.lbl2.SetLabel('The minimum measured angle was: ' + min +
                         ' degrees')
    nsth = str(round(float(d_list[2]), 2))
    window.lbl3.SetLabel('The 97th percentile of angles was: ' + nsth +
                         ' degrees')
    max = str(round(float(d_list[3]), 2))
    window.lbl4.SetLabel('The maximum measured angle was: ' + max + ' degrees')
    app.MainLoop()
    plt.show()


if __name__ == '__main__':
    run()

