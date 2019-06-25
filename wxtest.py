import wx

########################################################################
class MyFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="Close Me")
        panel = wx.Panel(self)

        closeBtn = wx.Button(panel, label="Close")
        closeBtn.Bind(wx.EVT_BUTTON, self.onClose)

    #----------------------------------------------------------------------
    def onClose(self, event):
        """"""
        self.Close()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    frame.Show()
    app.MainLoop()