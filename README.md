PyGB
=========

PyGB (Py-GUI-Background) is a fork of the PyAutoGUI to support background keyboard and mouse events to a specific window.

### Getting Started
Everything is the same as in the original PyAutoGUI, except for each function you can add a `window` argument to specify the window to send the event to (the window can be inactive, running in the background).

If the `window` argument is not specified, the event will be sent to the global event tap (same as original PyAutoGUI).

```python
import pygb

# Press key to a specific window
pygb.keyDown('a', window=859)
pygb.keyUp('a', window=859)

# Take screenshot of a specific window
img = pygb.screenshot('a', window=859)
```

### Other Changes
- Window support


```python


```

### Window resizing 
- `pygb.resize(window, width, height)` - resize a window to a specific size: https://stackoverflow.com/questions/70535283/how-can-i-resize-terminal-window-from-python