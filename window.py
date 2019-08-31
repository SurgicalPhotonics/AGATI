import wx
import os
import DataReader
import yaml
import csv
import cv2
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
        start_image = wx.Image('Splashscreen.jpg')
        start_image.Rescale(385, 425, quality=wx.IMAGE_QUALITY_HIGH)
        img = wx.BitmapFromImage(start_image)
        wx.StaticBitmap(self, -1, img, (0, 0), (img.GetWidth(), img.GetHeight()))


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


def vid_analysis(cfg, path, window, runnum, output_data, outfile):
    """Script calls for analysis of a single video."""
    scr.new_vid(cfg, path)
    data_path = scr.analyze(cfg, path)
    videotype = path[path.rfind('.'):]
    try:
        data = DataReader.read_data(data_path)
    except FileNotFoundError:
        d_path = os.path.join(path[:path.rfind('\\')], data_path[data_path.rfind('\\') + 1:])
        data = DataReader.read_data(d_path)
    T = Tracker(data)
    d_list = T.frame_by(path, runnum, outfile)
    output_data.append((path[path.rfind('\\') + 1:],
                        d_list[1], d_list[2], d_list[3], d_list[4], d_list[5],
                        d_list[6], d_list[7], d_list[8]))


def downsample(path):
    """Downsamples high res videos"""
    cap = cv2.VideoCapture(path)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if height <= 480:
        print('Already proper resolution')
        return path
    else:
        print('Downsampling to better resolution')
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frames = cap.get(cv2.CAP_PROP_FPS)
        r_height = 360
        ar = width / height
        r_width = int(ar * 360)
        fourcc = cv2.VideoWriter.fourcc('m', 'p', '4', 'v')
        name = path[:path.rfind('.')] + '_resized.mp4'
        writer = cv2.VideoWriter(name, fourcc, frames, (r_width, r_height))
        s, im = cap.read()
        while s:
            image = cv2.resize(im, (r_width, r_height))
            writer.write(image)
            s, im = cap.read()
        return name


def run(r=0):
    #filepath = os.path.join(os.getcwd(), 'vocal-Nat-2019-06-10', 'videos', 'video_data.csv')
    #f = open(filepath, 'w')
    #f.truncate()
    output_data = [('vidname', 'min angle', '3rd percentile angle',
                    '97th percentile angle', 'max angle', '97th percentile positive velocity',
                    '97th percentile negative velocity', '97th percentile positive acceleration',
                    '97th percentile negative acceleration')]
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
    wx.MessageBox('Please Select the directory in which you would like your '
                  'data to be stored', style=wx.OK | wx.ICON_INFORMATION)
    Tk().withdraw()
    outfile = filedialog.askdirectory()
    path, isdir = window.file_select()
    if isdir:
        runnum = r * 10
        for filename in os.listdir(path):
            if filename.endswith('.mp4') or filename.endswith('.avi'):
                filepath = os.path.join(path, filename)
                filepath = downsample(filepath)
                vid_analysis(cfg, filepath, window, runnum, output_data, outfile)
                runnum += 1
    else:
        path = downsample(path)
        vid_analysis(cfg, path, window, 0, output_data, outfile)
    #put data in vocal folder
    csv_data = os.path.join(outfile, 'video_data%d.csv' %r)
    with open(csv_data, 'w') as file:
        writer = csv.writer(file, delimiter=',')
        for set in output_data:
            writer.writerow([set[0], set[1], set[2], set[3], set[4], set[5],
                             set[6], set[7], set[8]])
    print('Your video data is stored here: ' + outfile)
    dlg = wx.MessageBox('Would you like to analyze more videos?', 'Continue', wx.YES_NO)
    if dlg == wx.YES:
        run(r=r + 1)
    else:
        pass
    app.MainLoop()


if __name__ == '__main__':
    run()

