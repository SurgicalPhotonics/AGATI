import wx
import os
import DataReader
import TrackingObjects
from tracker import Tracker

app = wx.App()
window = wx.Frame(None, -1, 'VCTrack')

if __name__ == '__main__':
    data = DataReader.read_data('vocal1DeepCut_resnet50_vocal_strobeMay8shuffle1_200000.h5')
    t = Tracker(data)
    t.frame_by()
    # Gonna do this bit with wx now
