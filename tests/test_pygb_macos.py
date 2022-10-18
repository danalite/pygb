import pygb
import sys
import time

# Slack
windowPID = 3253

if sys.platform == "darwin":
    from AppKit import NSWorkspace

    # https://stackoverflow.com/a/65766428
    # NSWorkspace.sharedWorkspace().runningApplications()
    # NSWorkspace.sharedWorkspace().frontmostApplication()
    # app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)

    from AppKit import NSApplicationActivateIgnoringOtherApps
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGWindowListExcludeDesktopElements,
        kCGNullWindowID
    )
elif sys.platform == "win32":
    from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect


class WindowInstance:
    def __init__(self, pid: int = 0, windwoID : int = 0, position: tuple = (0, 0),
                 dimX: int = 0, dimY: int = 0, app: str = "", title: str = ""):
        self.pid = pid
        self.windowID = windwoID
        self.lt = position
        self.wh = (dimX, dimY)
        self.owner = app
        self.title = title
    
    def __repr__(self):
        return f"WindowInstance(pid={self.pid}, WID={self.windowID}, lt={self.lt}, wh={self.wh}, owner={self.owner}, title={self.title})"

def getActiveApplicationName():
    return NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']

def activateWindow():
    runningApplications = NSWorkspace.sharedWorkspace().runningApplications()
    for app in runningApplications:
        # if getActiveApplicationName() == app.localizedName():
        if "Slack" in app.localizedName():
            app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)


def getActiveWindow():
    # https://stackoverflow.com/a/44229825
    # https://github.com/asweigart/PyGetWindow
    if sys.platform == "darwin":
        curr_app = NSWorkspace.sharedWorkspace().frontmostApplication()
        curr_pid = NSWorkspace.sharedWorkspace().activeApplication()[
            'NSApplicationProcessIdentifier']
        curr_app_name = curr_app.localizedName()

        options = kCGWindowListOptionOnScreenOnly 
        windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID)

        wi = None
        for window in windowList:
            pid = window['kCGWindowOwnerPID']

            windowNumber = window['kCGWindowNumber']
            ownerName = window['kCGWindowOwnerName']
            geometry = window['kCGWindowBounds']
            windowTitle = window.get('kCGWindowName', u'Unknown')

            if curr_pid == pid:
                title = windowTitle.encode('ascii', 'ignore')
                h, w, x, y = geometry["Height"], geometry["Width"], geometry["X"], geometry["Y"]
                if wi is not None:
                    new_wi = WindowInstance(pid, windowNumber, (x, y), w, h, ownerName, title)
                    print(f"(winGetActive) Multiple windows found for {curr_app_name}: {wi}, {new_wi}")
                    ow, oh = wi.wh
                    if ow < 100 or oh < 100:
                        if w > ow and h > oh:
                            wi = new_wi
                else:
                    wi = WindowInstance(pid, windowNumber, (x, y), w, h, ownerName, title)

    elif sys.platform == "win32":
        hwnd = GetForegroundWindow()
        title = GetWindowText(hwnd)
        x1, y1, x2, y2 = GetWindowRect(hwnd)
        wi = WindowInstance(hwnd, (x1, y1), x2-x1, y2-y1, title, "")

    return wi

# Key event to a specific window
# pygb.keyDown("s", window=windowPID)


time.sleep(3)
print(getActiveWindow())

# pygb.hotkey("f1", window=windowPID, interval = 0.05)
pygb.hotkey("command", "G", window=windowPID, interval = 0.05)
pygb.hotkey("command", "Enter", window=windowPID, interval = 0.05)
pygb.hotkey("lshift", "A", window=windowPID)

pygb.moveTo(62, 22, duration=0.5)
activateWindow()