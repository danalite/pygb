import pygb
windowPID = 474

# Key event to a specific window
pygb.keyDown("s", window=windowPID)

print(pygb.getActiveWindow())

pygb.write("top", window=windowPID)
pygb.hotkey("Enter", window=windowPID, interval = 0.5)
pygb.hotkey("q", window=windowPID, interval = 0.05)
pygb.write("echo 'Top is done'", window=windowPID)
pygb.press("Enter", window=windowPID)

# pygb.moveTo(62, 22, duration=0.5)
pygb.activateWindow("Slack")