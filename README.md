PyGB
=========

PyGB (Py-GUI-Background) is a fork of the PyAutoGUI to support background keyboard and mouse events to a specific window.

### Examples

```python
import pygb

# Press key
pygb.keyDown('a', window='Notepad')
pygb.keyUp('a', window='Notepad')


# https://stackoverflow.com/questions/57041904/macos-screenshot-a-minimised-window-with-python
pygb.keyDown('a'

```