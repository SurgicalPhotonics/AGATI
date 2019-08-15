import wx
import os
import DataReader
import yaml
import csv
import matplotlib.pyplot as plt
from tracker import Tracker
from tkinter import*
from tkinter import filedialog
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

    def file_select(self) -> (any, bool):
        """Prompts user to select input file for analysis."""
        dlg = wx.MessageBox('Would you like to analyze a new video?', 'Confirm',
                            wx.YES_NO)
        if dlg == wx.YES:
            dlg = wx.MessageBox('Would you like to analyze a directory of '
                                'videos?', 'Confirm', wx.YES_NO)
            if dlg == wx.YES:
                Tk().withdraw()
                return filedialog.askdirectory(), True
            else:
                Tk().withdraw()
                return askopenfilename(), False
        else:
            dlg = wx.MessageBox('Would you like to close the program?', 'Confirm',
                                wx.YES_NO)
            if dlg == wx.YES:
                self.quit()
            else:
                self.file_select()


def vid_analysis(cfg, path, window, runnum, output_data):
    """Script calls for analysis of a single video."""
    scr.new_vid(cfg, path)
    data_path = scr.analyze(cfg, path)
    vid_path = scr.label(cfg, path)
    videotype = vid_path[vid_path.rfind('.'):]
    try:
        data = DataReader.read_data(data_path)
    except FileNotFoundError:
        d_path = os.path.join(path[:path.rfind('\\')], data_path[data_path.rfind('\\') + 1:])
        data = DataReader.read_data(d_path)
        vid_path = d_path[:d_path.rfind('Deep')] + videotype
    T = Tracker(data)
    d_list = T.frame_by(vid_path, runnum)
    window.lbl.SetLabel('Your video with printed lines can be found here: ' +
            d_list[0])
    min = str(round(float(d_list[1]), 2))
    window.lbl2.SetLabel('The minimum measured angle was: ' + min + ' degrees')
    nsth = str(round(float(d_list[2]), 2))
    window.lbl3.SetLabel('The 97th percentile of angles was: ' + nsth +
                         ' degrees')
    max = str(round(float(d_list[3]), 2))
    window.lbl4.SetLabel('The maximum measured angle was: ' + max + ' degrees')
    output_data.append((vid_path[vid_path.rfind('\\') + 1: path.find('Deep')], min, nsth, max))


def run():
    #filepath = os.path.join(os.getcwd(), 'vocal-Nat-2019-06-10', 'videos', 'video_data.csv')
    #f = open(filepath, 'w')
    #f.truncate()
    output_data = [('vidname', 'min angle', 'max angle', '97th percentile angle')]
    name = os.path.dirname(os.path.abspath(__file__))
    cfg = os.path.join(name, 'vocal_fold-Nat-2019-08-07')
    file_name = os.path.join(cfg, 'config.yaml')
    stream = open(file_name, 'r')
    data = yaml.load(stream)
    data['project_path'] = cfg
    with open(file_name, 'w') as yaml_file:
        yaml_file.write(yaml.dump(data, default_flow_style=False))
    app = wx.App(False)
    window = Window()
    window.Show()
    path, isdir = window.file_select()
    if isdir:
        runnum = 0
        for filename in os.listdir(path):
            if filename.endswith('.mp4') or filename.endswith('.avi'):
                filepath = os.path.join(path, filename)
                vid_analysis(cfg, filepath, window, runnum, output_data)
                runnum += 1
    else:
        vid_analysis(cfg, path, window, 0, output_data)
    with open('video_data.csv', 'w') as file:
        writer = csv.writer(file, delimiter=',')
        for set in output_data:
            writer.writerow([set[0], set[1], set[2], set[3]])
    app.MainLoop()


if __name__ == '__main__':
    run()

