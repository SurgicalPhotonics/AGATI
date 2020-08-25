print("Initializing. This may take a minute.")
print("Importing wx")
import wx
print("Importing utilities")
from os import path as ospath
from os import listdir, remove, unlink
import DataReader
from csv import writer as csvwriter
print("Importing OpenCV")
from cv2 import CAP_PROP_FPS, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, VideoCapture, VideoWriter, resize
print("Filtering warnings")
from warnings import filterwarnings, simplefilter
print("Checking system variables")
import sys
print("Filtering warnings")
filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)
simplefilter(action='ignore', category=FutureWarning)

"""CPU
print("Importing Tensorflow")
import tensorflow as tf
print("Filtering tensorflow warnings")
if type(tf.contrib) != type(tf): tf.contrib._warning = None
print("Importing yaml")
"""
import yaml
print("Importing AGATI functions")
from tracker import Tracker
print("Importing DeepLabCut functions. This step may take longer than others.")
import dlc_script as scr


class Window(wx.Frame):
    """Base of GUI. Displays AGATI Image. Added functionality coming."""
    def __init__(self):
        x, y = wx.GetDisplaySize()
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title='AGATI', pos=(100, 100), size=(x/2, y/2))
        #impath = ospath.dirname(ospath.realpath(__file__)) #uncomment this if running as python code
        impath = sys._MEIPASS #for pyinstaller compile.
        start_image = wx.Image(ospath.join(impath, 'Splashscreen.jpg'))
        start_image.Rescale(x/2, y/2, quality=wx.IMAGE_QUALITY_HIGH)
        img = wx.Bitmap(start_image)
        wx.StaticBitmap(self, -1, img, (0, 0), (img.GetWidth(), img.GetHeight()))

    def quit(self):
        self.Close()

    def file_select(self) -> (any, bool):
        """Prompts user to select input file for analysis."""
        dlg = wx.MessageBox('Would you like to analyze a new video?', 'Confirm',
                            wx.YES_NO)
        if dlg == wx.YES:
            dlg = wx.MessageBox('Would you like to analyze a directory of videos?', 'Confirm', wx.YES_NO)
            if dlg == wx.YES:
                fd = wx.DirDialog(self, "Choose Input Directory", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
                if fd.ShowModal() == wx.ID_OK:
                    path = fd.GetPath()
                    fd.Destroy()
                    return path, True
            else:
                fd = wx.FileDialog(self, "Choose Input Video", style=wx.FD_DEFAULT_STYLE | wx.FD_FILE_MUST_EXIST)
                if fd.ShowModal() == wx.ID_OK:
                    path = fd.GetPath()
                    fd.Destroy()
                    return path, False
        else:
            dlg = wx.MessageBox('Would you like to close the program?', 'Confirm',
                                wx.YES_NO)
            if dlg == wx.YES:
                self.quit()
            else:
                self.file_select()


def vid_analysis(cfg, path, runnum, output_data, outfile):
    """Script calls for analysis of a single video."""
    scr.new_vid(cfg, path)
    data_path = scr.analyze(cfg, path)
    try:
        data = DataReader.read_data(data_path)
    except FileNotFoundError:
        location = ospath.split(ospath.split(data_path)[0])[1]
        d_path = ospath.join(path[:path.rfind('\\')], location + data_path[data_path.rfind('\\') + 1:])
        data = DataReader.read_data(d_path)
    T = Tracker(data)
    name = path[path.rfind('\\') + 1:path.rfind('.')]
    d_list = T.frame_by(path, runnum, outfile, name)
    output_data.append((path[path.rfind('\\') + 1:], d_list[1], d_list[2], d_list[3], d_list[4], d_list[5], d_list[6],
                        d_list[7], d_list[8]))


def downsample(path):
    """Downsamples high res videos to more manageable resolution for DeepLabCut"""
    cap = VideoCapture(path)
    height = int(cap.get(CAP_PROP_FRAME_HEIGHT))
    if height <= 480:
        print('Already proper resolution')
        return path
    else:
        print('Downsampling to better resolution for analysis.')
        width = int(cap.get(CAP_PROP_FRAME_WIDTH))
        frames = cap.get(CAP_PROP_FPS)
        r_height = 360
        ar = width / height
        r_width = int(ar * 360)
        fourcc = VideoWriter.fourcc('m', 'p', '4', 'v')
        name = path[:path.rfind('.')] + '_resized.mp4'
        writer = VideoWriter(name, fourcc, frames, (r_width, r_height))
        s, im = cap.read()
        while s:
            image = resize(im, (r_width, r_height))
            writer.write(image)
            s, im = cap.read()
        return name


def ask(parent=None, message=''):
    dlg = wx.TextEntryDialog(parent, message)
    dlg.ShowModal()
    result = dlg.GetValue()
    dlg.Destroy()
    return result


def run(r=0):
    print("Dependencies Loaded")
    output_data = [('vidname', 'min angle', '3rd percentile angle',
                    '97th percentile angle', 'max angle', '97th percentile positive velocity',
                    '97th percentile negative velocity', '97th percentile positive acceleration',
                    '97th percentile negative acceleration')]
    print("Loading Project Settings")
    name = ospath.dirname(ospath.abspath(__file__))
    cfg = ospath.join(name, 'vocal_fold-Nat-2019-08-07')
    file_name = ospath.join(cfg, 'config.yaml')
    try:
        stream = open(file_name, 'r')
    except FileNotFoundError:
        name = sys._MEIPASS
        cfg = ospath.join(name, 'vocal_fold-Nat-2019-08-07')
        file_name = ospath.join(cfg, 'config.yaml')
        stream = open(file_name, 'r')
    print("Checking File Paths")
    data = yaml.load(stream, Loader=yaml.FullLoader)
    if data['project_path'] != cfg:
        data['project_path'] = cfg
        with open(file_name, 'w') as yaml_file:
            yaml_file.write(yaml.dump(data, default_flow_style=False))
    print("Initializing GUI")
    app = wx.App(False)
    window = Window()
    window.Show()
    wx.MessageBox('Please Select the directory in which you would like your '
                  'data to be stored', style=wx.OK | wx.ICON_INFORMATION)
    fd = wx.DirDialog(None, "Choose Output Directory", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
    outfile = fd.GetPath()
    if fd.ShowModal() == wx.ID_OK:
        outfile = fd.GetPath()
        fd.Destroy()
    path, isdir = window.file_select()
    if isdir:
        runnum = r * 10
        for filename in listdir(path):
            if filename.endswith('.mp4') or filename.endswith('.avi'):
                filepath = ospath.join(path, filename)
                filepath = downsample(filepath)
                vid_analysis(cfg, filepath, runnum, output_data, outfile)
                runnum += 1
    else:
        path = downsample(path)
        vid_analysis(cfg, path, 0, output_data, outfile)
    #put data in vocal folder
    csv_data = ospath.join(outfile, 'ensemble_statistics.csv')
    with open(csv_data, 'w') as file:
        writer = csvwriter(file, delimiter=',')
        for set in output_data:
            writer.writerow([set[0], set[1], set[2], set[3], set[4], set[5],
                             set[6], set[7], set[8]])
    print('Your video data is stored here: ' + outfile)
    #Delete videos added to DLC videos folder
    vfolder = ospath.join(cfg, 'videos')
    for filename in listdir(vfolder):
        filepath = ospath.join(vfolder, filename)
        if ospath.islink(filepath):
            unlink(filepath)
        if ospath.isfile(filepath):
            remove(filepath)
    for filename in listdir(outfile):
        filepath = ospath.join(outfile, filename)
        if filename.endswith('_resized.mp4'):
            remove(filepath)

    dlg = wx.MessageBox('Would you like to analyze more videos?', 'Continue', wx.YES_NO)
    if dlg == wx.YES:
        run(r=r + 1)
    else:
        window.quit()
    app.MainLoop()


if __name__ == '__main__':
    run()

