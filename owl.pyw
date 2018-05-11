
"""
Originally from https://github.com/seanbuscay
"""

import wx
import wx.adv
import os
import sys
import time
import psutil
import win32api
from win32gui import GetWindowText, GetForegroundWindow
from win32process import GetWindowThreadProcessId
import datetime
import jsonlogwrite as logwrite

# Dont consider it idle if there hasnt been input for this long
MIN_IDLE_SECONDS = 30
LOG_PATH = os.path.expanduser('~/owl_logs')


def process_info(window_handle):
    "Return process info about a window handle id"
    pprocess = GetWindowThreadProcessId(window_handle)
    p = psutil.Process(pprocess[1])
    return p


class TaskBarApp(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title, size=(1, 1),
                          style=wx.FRAME_NO_TASKBAR | wx.NO_FULL_REPAINT_ON_RESIZE)

        if getattr(sys, 'frozen', False):
            self.enabled_icon = wx.Icon(
                os.path.join(sys._MEIPASS, 'logon.ico'))
            self.disabled_icon = wx.Icon(
                os.path.join(sys._MEIPASS, 'logoff.ico'))
        else:
            self.enabled_icon = wx.Icon(
                os.path.join(os.path.abspath(), 'logon.ico'))
            self.disabled_icon = wx.Icon(
                os.path.join(os.path.abspath(), 'logoff.ico'))

        self.tbicon = wx.adv.TaskBarIcon()
        self.tbicon.SetIcon(self.enabled_icon, 'Logging')
        self.tbicon.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
        self.tbicon.Bind(wx.adv.EVT_TASKBAR_RIGHT_UP, self.OnTaskBarRightClick)

        # 1s repeating timer
        self.timer_running = True
        self.timer_id = wx.NewId()
        self.Bind(wx.EVT_TIMER, self.on_timer, id=self.timer_id)
        self.timer = wx.Timer(self, self.timer_id)
        self.timer.Start(1000)

        self.Show(True)
        self.last_input = 0
        self.last_active = time.time()
        self.is_idle = False
        self.update_logfile()
        self.logger_check = 0

        # Startup logging
        logwrite.write(dict(log_message="Startup"), self.logfile)
        self.new_active_window()

    def update_logfile(self):
        if not os.path.isdir(LOG_PATH):
            os.mkdir(LOG_PATH)
        self.logfile = os.path.join(LOG_PATH, datetime.datetime.now().strftime('%Y%m%d.json'))

    def OnTaskBarLeftDClick(self, evt):
        "Double click toggles logging on/off"
        if self.timer_running:
            self.StopTimer()
            self.timer_running = False
            self.tbicon.SetIcon(self.disabled_icon, 'Not Logging')

        else:
            self.RestartTimer()
            self.timer_running = True
            self.tbicon.SetIcon(self.enabled_icon, 'Logging')

    def OnTaskBarRightClick(self, evt):
        logwrite.write(dict(log_message="user shutdown, right clicked"), self.logfile)
        self.StopTimer()
        self.tbicon.Destroy()
        self.Close(True)
        wx.Exit()

    def RestartTimer(self):
        try:
            self.timer.Start(1000)
            logwrite.write(dict(log_message="Restarting timer"), self.logfile)
            self.new_active_window()
        except Exception as e:
            pass

    def StopTimer(self):
        try:
            self.timer.Stop()
            logwrite.write(self.data, self.logfile)
            logwrite.write(dict(log_message="Timer stopped"), self.logfile)
            self.new_active_window()
        except Exception as e:
            pass

    def on_timer(self, evt):
        if not self.data:
            return self.new_active_window()

        # last_input the tick count of last input (tick count is milliseconds since boot)
        last_input = win32api.GetLastInputInfo()

        nowtime = time.time()

        # if we got some activity, see if it's been long enough
        # since the last time to count as idle
        if last_input != self.last_input:
            idle_secs = nowtime - self.last_active
            if idle_secs > MIN_IDLE_SECONDS:
                self.data['idle_seconds'] += idle_secs
            self.last_active = nowtime

        self.last_input = last_input

        # If current window is different from the last time we checked, log the info about
        # the previous one and start tracking the current one
        active_hwnd = GetForegroundWindow()
        window_title = GetWindowText(active_hwnd)
        if self.data['hwnd'] != active_hwnd or self.data['window_title'] != window_title:
            self.data['end_timestamp'] = str(datetime.datetime.now())
            logwrite.write(self.data, self.logfile)
            self.new_active_window()

        # update the log filename every 120s
        self.logger_check += 1
        if self.logger_check >= 120:
            self.update_logfile()
            self.logger_check = 0

    def new_active_window(self):
        """Capture the info about the newly active window so when it changes
        we can output how long it was active
        """
        self.data = {}

        try:
            self.data['user'] = os.environ.get('USERNAME', '_NOUSER_')
            self.data['hostname'] = os.environ.get('COMPUTERNAME', '_NOHOSTNAME_')

            active_hwnd = GetForegroundWindow()
            self.data['hwnd'] = active_hwnd
            self.data['window_title'] = GetWindowText(active_hwnd)

            procinfo = process_info(active_hwnd)
            self.data['process_name'] = procinfo.name()
            self.data['pid'] = procinfo.pid
            self.data['idle_seconds'] = 0.0
            self.data['start_timestamp'] = str(datetime.datetime.now())
        except Exception as e:
            print("Caught exception trying to get active window info: " + str(e))
            self.data = {}


class MyApp(wx.App):
    def OnInit(self):
        frame = TaskBarApp(None, -1, ' ')
        frame.Center(wx.BOTH)
        frame.Show(True)
        return True


def main():
    app = MyApp(0)
    app.MainLoop()


if __name__ == '__main__':
    main()
