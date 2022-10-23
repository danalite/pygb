from __future__ import division, print_function

import os
import random
import sys
import threading
import time
import unittest
import doctest
from collections import namedtuple  # Added in Python 2.6.

import pygb

# Make the cwd the folder that this test_pygb.py file resides in:
scriptFolder = os.path.dirname(os.path.realpath(__file__))
os.chdir(scriptFolder)

runningOnPython2 = sys.version_info[0] == 2

if runningOnPython2:
    INPUT_FUNC = raw_input
else:
    INPUT_FUNC = input


try:
    import pyscreeze
except:
    assert False, "The PyScreeze module must be installed to complete the tests: pip install pyscreeze"


# TODO - note that currently most of the click-related functionality is not tested.


class P(namedtuple("P", ["x", "y"])):
    """Simple, immutable, 2D point/vector class, including some basic
    arithmetic functions.
    """

    def __str__(self):
        return "{0},{1}".format(self.x, self.y)

    def __repr__(self):
        return "P({0}, {1})".format(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x and self.y != other.y

    def __add__(self, other):
        return P(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return P(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return P(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __floordiv__(self, other):
        return P(self.x // other, self.y // other)

    def __truediv__(self, other):
        return P(self.x / other, self.y / other)

    def __neg__(self):
        return P(-self.x, -self.y)

    def __pos__(self):
        return self

    def __neg__(self):
        return P(abs(self.x), abs(self.y))


class TestGeneral(unittest.TestCase):
    def setUp(self):
        self.oldFailsafeSetting = pygb.FAILSAFE
        pygb.FAILSAFE = False
        pygb.moveTo(42, 42)  # make sure failsafe isn't triggered during this test
        pygb.FAILSAFE = True

    def tearDown(self):
        pygb.FAILSAFE = self.oldFailsafeSetting

    def test_accessibleNames(self):
        # Check that all the functions are defined.

        # mouse-related API
        pygb.moveTo
        pygb.moveRel
        pygb.dragTo
        pygb.dragRel
        pygb.mouseDown
        pygb.mouseUp
        pygb.click
        pygb.rightClick
        pygb.doubleClick
        pygb.tripleClick

        # keyboard-related API
        pygb.typewrite
        pygb.hotkey
        pygb.keyDown
        pygb.keyUp
        pygb.press
        pygb.hold

        # The functions implemented in the platform-specific modules should also show up in the pygb namespace:
        pygb.position
        pygb.size
        pygb.scroll
        pygb.hscroll
        pygb.vscroll

        # util API
        pygb.KEYBOARD_KEYS
        pygb.isShiftCharacter

        # Screenshot-related API
        pygb.locateAll
        pygb.locate
        pygb.locateOnScreen
        pygb.locateAllOnScreen
        pygb.locateCenterOnScreen
        pygb.center
        pygb.pixelMatchesColor
        pygb.pixel
        pygb.screenshot
        pygb.grab

        # Tweening-related API
        pygb.getPointOnLine
        pygb.linear

    def test_size(self):
        width, height = pygb.size()

        self.assertTrue(isinstance(width, int), "Type of width is %s" % (type(width)))
        self.assertTrue(isinstance(height, int), "Type of height is %s" % (type(height)))
        self.assertTrue(width > 0, "Width is set to %s" % (width))
        self.assertTrue(height > 0, "Height is set to %s" % (height))

    def test_position(self):
        mousex, mousey = pygb.position()

        self.assertTrue(isinstance(mousex, int), "Type of mousex is %s" % (type(mousex)))
        self.assertTrue(isinstance(mousey, int), "Type of mousey is %s" % (type(mousey)))

        # Test passing x and y arguments to position().
        pygb.moveTo(mousex + 1, mousey + 1)
        x, y = pygb.position(mousex, None)
        self.assertEqual(x, mousex)
        self.assertNotEqual(y, mousey)

        x, y = pygb.position(None, mousey)
        self.assertNotEqual(x, mousex)
        self.assertEqual(y, mousey)

    def test_onScreen(self):
        zero = P(0, 0)
        xone = P(1, 0)
        yone = P(0, 1)
        size = P(*pygb.size())
        half = size / 2

        on_screen = [zero, zero + xone, zero + yone, zero + xone + yone, half, size - xone - yone]
        off_screen = [zero - xone, zero - yone, zero - xone - yone, size - xone, size - yone, size]

        for value, coords in [(True, on_screen), (False, off_screen)]:
            for coord in coords:
                self.assertEqual(
                    value,
                    pygb.onScreen(*coord),
                    "onScreen({0}, {1}) should be {2}".format(coord.x, coord.y, value),
                )
                self.assertEqual(
                    value,
                    pygb.onScreen(list(coord)),
                    "onScreen([{0}, {1}]) should be {2}".format(coord.x, coord.y, value),
                )
                self.assertEqual(
                    value,
                    pygb.onScreen(tuple(coord)),
                    "onScreen(({0}, {1})) should be {2}".format(coord.x, coord.y, value),
                )
                self.assertEqual(
                    value, pygb.onScreen(coord), "onScreen({0}) should be {1}".format(repr(coord), value)
                )

        # These raise PyGBException.
        with self.assertRaises(pygb.PyGBException):
            pygb.onScreen([0, 0], 0)
        with self.assertRaises(pygb.PyGBException):
            pygb.onScreen((0, 0), 0)

    def test_pause(self):
        oldValue = pygb.PAUSE

        startTime = time.time()
        pygb.PAUSE = 0.35  # there should be a 0.35 second pause after each call
        pygb.moveTo(1, 1)
        pygb.moveRel(0, 1)
        pygb.moveTo(1, 1)

        elapsed = time.time() - startTime
        self.assertTrue(1.0 < elapsed < 1.1, "Took %s seconds, expected 1.0 < 1.1 seconds." % (elapsed))

        pygb.PAUSE = oldValue  # restore the old PAUSE value


class TestHelperFunctions(unittest.TestCase):
    def test__normalizeXYArgs(self):
        self.assertEqual(pygb._normalizeXYArgs(1, 2), pygb.Point(x=1, y=2))
        self.assertEqual(pygb._normalizeXYArgs((1, 2), None), pygb.Point(x=1, y=2))
        self.assertEqual(pygb._normalizeXYArgs([1, 2], None), pygb.Point(x=1, y=2))

        pygb.useImageNotFoundException()
        with self.assertRaises(pygb.ImageNotFoundException):
            pygb._normalizeXYArgs("100x100blueimage.png", None)
        pygb.useImageNotFoundException(False)
        self.assertEqual(pygb._normalizeXYArgs("100x100blueimage.png", None), None)


class TestDoctests(unittest.TestCase):
    def test_doctests(self):
        doctest.testmod(pygb)


class TestMouse(unittest.TestCase):
    # NOTE - The user moving the mouse during many of these tests will cause them to fail.

    # There is no need to test all tweening functions.
    TWEENS = [
        "linear",
        "easeInElastic",
        "easeOutElastic",
        "easeInOutElastic",
        "easeInBack",
        "easeOutBack",
        "easeInOutBack",
    ]

    def setUp(self):
        self.oldFailsafeSetting = pygb.FAILSAFE
        self.center = P(*pygb.size()) // 2

        pygb.FAILSAFE = False
        pygb.moveTo(*self.center)  # make sure failsafe isn't triggered during this test
        pygb.FAILSAFE = True

    def tearDown(self):
        pygb.FAILSAFE = self.oldFailsafeSetting

    def test_moveTo(self):
        # moving the mouse
        desired = self.center
        pygb.moveTo(*desired)
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # no coordinate specified (should be a NO-OP)
        pygb.moveTo(None, None)
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # moving the mouse to a new location
        desired += P(42, 42)
        pygb.moveTo(*desired)
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # moving the mouse over time (1/5 second)
        desired -= P(42, 42)
        pygb.moveTo(desired.x, desired.y, duration=0.2)
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # Passing a list instead of separate x and y.
        desired += P(42, 42)
        pygb.moveTo(list(desired))
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # Passing a tuple instead of separate x and y.
        desired += P(42, 42)
        pygb.moveTo(tuple(desired))
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # Passing a sequence-like object instead of separate x and y.
        desired -= P(42, 42)
        pygb.moveTo(desired)
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

    def test_moveToWithTween(self):
        origin = self.center - P(100, 100)
        destination = self.center + P(100, 100)

        def resetMouse():
            pygb.moveTo(*origin)
            mousepos = P(*pygb.position())
            self.assertEqual(mousepos, origin)

        for tweenName in self.TWEENS:
            tweenFunc = getattr(pygb, tweenName)
            resetMouse()
            pygb.moveTo(destination.x, destination.y, duration=pygb.MINIMUM_DURATION * 2, tween=tweenFunc)
            mousepos = P(*pygb.position())
            self.assertEqual(
                mousepos,
                destination,
                "%s tween move failed. mousepos set to %s instead of %s" % (tweenName, mousepos, destination),
            )

    def test_moveRel(self):
        # start at the center
        desired = self.center
        pygb.moveTo(*desired)
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # move down and right
        desired += P(42, 42)
        pygb.moveRel(42, 42)
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # move up and left
        desired -= P(42, 42)
        pygb.moveRel(-42, -42)
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # move right
        desired += P(42, 0)
        pygb.moveRel(42, 0)
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # move down
        desired += P(0, 42)
        pygb.moveRel(0, 42)
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # move left
        desired += P(-42, 0)
        pygb.moveRel(-42, 0)
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # move up
        desired += P(0, -42)
        pygb.moveRel(0, -42)
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # Passing a list instead of separate x and y.
        desired += P(42, 42)
        pygb.moveRel([42, 42])
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # Passing a tuple instead of separate x and y.
        desired -= P(42, 42)
        pygb.moveRel((-42, -42))
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

        # Passing a sequence-like object instead of separate x and y.
        desired += P(42, 42)
        pygb.moveRel(P(42, 42))
        mousepos = P(*pygb.position())
        self.assertEqual(mousepos, desired)

    def test_moveRelWithTween(self):
        origin = self.center - P(100, 100)
        delta = P(200, 200)
        destination = origin + delta

        def resetMouse():
            pygb.moveTo(*origin)
            mousepos = P(*pygb.position())
            self.assertEqual(mousepos, origin)

        for tweenName in self.TWEENS:
            tweenFunc = getattr(pygb, tweenName)
            resetMouse()
            pygb.moveRel(delta.x, delta.y, duration=pygb.MINIMUM_DURATION * 2, tween=tweenFunc)
            mousepos = P(*pygb.position())
            self.assertEqual(
                mousepos,
                destination,
                "%s tween move failed. mousepos set to %s instead of %s" % (tweenName, mousepos, destination),
            )

    def test_scroll(self):
        # TODO - currently this just checks that scrolling doesn't result in an error.
        pygb.scroll(1)
        pygb.scroll(-1)
        pygb.hscroll(1)
        pygb.hscroll(-1)
        pygb.vscroll(1)
        pygb.vscroll(-1)


class TestRun(unittest.TestCase):
    def test_getNumberToken(self):
        self.assertEqual(pygb._getNumberToken("5hello"), "5")
        self.assertEqual(pygb._getNumberToken("-5hello"), "-5")
        self.assertEqual(pygb._getNumberToken("+5hello"), "+5")
        self.assertEqual(pygb._getNumberToken("5.5hello"), "5.5")
        self.assertEqual(pygb._getNumberToken("+5.5hello"), "+5.5")
        self.assertEqual(pygb._getNumberToken("-5.5hello"), "-5.5")
        self.assertEqual(pygb._getNumberToken("  5hello"), "  5")
        self.assertEqual(pygb._getNumberToken("  -5hello"), "  -5")
        self.assertEqual(pygb._getNumberToken("  +5hello"), "  +5")
        self.assertEqual(pygb._getNumberToken("  5.5hello"), "  5.5")
        self.assertEqual(pygb._getNumberToken("  +5.5hello"), "  +5.5")
        self.assertEqual(pygb._getNumberToken("  -5.5hello"), "  -5.5")

        with self.assertRaises(pygb.PyGBException):
            pygb._getNumberToken("")  # Blank string and no number.
        with self.assertRaises(pygb.PyGBException):
            pygb._getNumberToken("hello")  # Missing a number.
        with self.assertRaises(pygb.PyGBException):
            pygb._getNumberToken("    ")  # Missing a number.
        with self.assertRaises(pygb.PyGBException):
            pygb._getNumberToken("hello 42")  # Number is not at the start.

    def test_getQuotedStringToken(self):
        self.assertEqual(pygb._getQuotedStringToken("'hello'world"), "'hello'")
        self.assertEqual(pygb._getQuotedStringToken("''world"), "''")
        self.assertEqual(pygb._getQuotedStringToken("  'hello'world"), "  'hello'")

        with self.assertRaises(pygb.PyGBException):
            pygb._getQuotedStringToken("xyz")  # No quotes.
        with self.assertRaises(pygb.PyGBException):
            pygb._getQuotedStringToken("xyz")  # No quotes.
        with self.assertRaises(pygb.PyGBException):
            pygb._getQuotedStringToken("  xyz")  # No quotes, spaces in front.
        with self.assertRaises(pygb.PyGBException):
            pygb._getQuotedStringToken("'xyz")  # Start quote only.
        with self.assertRaises(pygb.PyGBException):
            pygb._getQuotedStringToken("xyz'")  # End quote only.
        with self.assertRaises(pygb.PyGBException):
            pygb._getQuotedStringToken('"xyz"')  # Double quotes don't count.
        with self.assertRaises(pygb.PyGBException):
            pygb._getQuotedStringToken("")  # Blank string.
        with self.assertRaises(pygb.PyGBException):
            pygb._getQuotedStringToken("xyz 'hello'")  # Quoted string is not at the start.

    def test_getCommaToken(self):
        self.assertEqual(pygb._getCommaToken(","), ",")
        self.assertEqual(pygb._getCommaToken("  ,"), "  ,")

        with self.assertRaises(pygb.PyGBException):
            pygb._getCommaToken("")  # Blank string.
        with self.assertRaises(pygb.PyGBException):
            pygb._getCommaToken("hello,")  # Comma is not at the start.
        with self.assertRaises(pygb.PyGBException):
            pygb._getCommaToken("hello")  # No comma.
        with self.assertRaises(pygb.PyGBException):
            pygb._getCommaToken("    ")  # No comma.

    def test_getParensCommandStrToken(self):
        self.assertEqual(pygb._getParensCommandStrToken("()"), "()")
        self.assertEqual(pygb._getParensCommandStrToken("  ()"), "  ()")
        self.assertEqual(pygb._getParensCommandStrToken("()hello"), "()")
        self.assertEqual(pygb._getParensCommandStrToken("  ()hello"), "  ()")
        self.assertEqual(pygb._getParensCommandStrToken("(hello)world"), "(hello)")
        self.assertEqual(pygb._getParensCommandStrToken("  (hello)world"), "  (hello)")
        self.assertEqual(pygb._getParensCommandStrToken("(he(ll)(o))world"), "(he(ll)(o))")
        self.assertEqual(pygb._getParensCommandStrToken("  (he(ll)(o))world"), "  (he(ll)(o))")

        self.assertEqual(
            pygb._getParensCommandStrToken("(he(ll)(o)))world"), "(he(ll)(o))"
        )  # Extra close parentheses.
        self.assertEqual(
            pygb._getParensCommandStrToken("  (he(ll)(o)))world"), "  (he(ll)(o))"
        )  # Extra close parentheses.

        with self.assertRaises(pygb.PyGBException):
            pygb._getParensCommandStrToken("")  # Blank string.
        with self.assertRaises(pygb.PyGBException):
            pygb._getParensCommandStrToken("  ")  # No parens.
        with self.assertRaises(pygb.PyGBException):
            pygb._getParensCommandStrToken("hello")  # No parens
        with self.assertRaises(pygb.PyGBException):
            pygb._getParensCommandStrToken(" (")  # No close parenthesis.
        with self.assertRaises(pygb.PyGBException):
            pygb._getParensCommandStrToken("(he(ll)o")  # Not enough close parentheses.
        with self.assertRaises(pygb.PyGBException):
            pygb._getParensCommandStrToken("")  # Blank string.

    def test_tokenizeCommandStr(self):
        self.assertEqual(pygb._tokenizeCommandStr(""), [])  # Empty command string.
        self.assertEqual(pygb._tokenizeCommandStr("  "), [])  # Whitespace only command string.
        self.assertEqual(pygb._tokenizeCommandStr("c"), ["c"])
        self.assertEqual(pygb._tokenizeCommandStr("  c  "), ["c"])
        self.assertEqual(pygb._tokenizeCommandStr("ccc"), ["c", "c", "c"])
        self.assertEqual(pygb._tokenizeCommandStr("  c  c  c  "), ["c", "c", "c"])
        self.assertEqual(pygb._tokenizeCommandStr("clmr"), ["c", "l", "m", "r"])
        self.assertEqual(pygb._tokenizeCommandStr("susdss"), ["su", "sd", "ss"])
        self.assertEqual(pygb._tokenizeCommandStr(" su sd ss "), ["su", "sd", "ss"])
        self.assertEqual(pygb._tokenizeCommandStr("clmrsusdss"), ["c", "l", "m", "r", "su", "sd", "ss"])

        # Do a whole bunch of tests with random no-argument commands with random whitespace.
        random.seed(42)
        for i in range(100):
            commands = []
            commands.extend(["c"] * random.randint(0, 9))
            commands.extend(["l"] * random.randint(0, 9))
            commands.extend(["m"] * random.randint(0, 9))
            commands.extend(["r"] * random.randint(0, 9))
            commands.extend(["su"] * random.randint(0, 9))
            commands.extend(["sd"] * random.randint(0, 9))
            commands.extend(["ss"] * random.randint(0, 9))
            random.shuffle(commands)
            commandStr = []
            for command in commands:
                commandStr.append(command)
                commandStr.append(" " * random.randint(0, 9))
            commandStr = "".join(commandStr)
            self.assertEqual(pygb._tokenizeCommandStr(commandStr), commands)

        self.assertEqual(pygb._tokenizeCommandStr("g10,10"), ["g", "10", "10"])
        self.assertEqual(pygb._tokenizeCommandStr("g 10,10"), ["g", "10", "10"])
        self.assertEqual(pygb._tokenizeCommandStr("g10 ,10"), ["g", "10", "10"])
        self.assertEqual(pygb._tokenizeCommandStr("g10, 10"), ["g", "10", "10"])
        self.assertEqual(pygb._tokenizeCommandStr(" g 10 , 10 "), ["g", "10", "10"])
        self.assertEqual(pygb._tokenizeCommandStr("  g  10  ,  10  "), ["g", "10", "10"])

        self.assertEqual(pygb._tokenizeCommandStr("g+10,+10"), ["g", "+10", "+10"])
        self.assertEqual(pygb._tokenizeCommandStr("g +10,+10"), ["g", "+10", "+10"])
        self.assertEqual(pygb._tokenizeCommandStr("g+10 ,+10"), ["g", "+10", "+10"])
        self.assertEqual(pygb._tokenizeCommandStr("g+10, +10"), ["g", "+10", "+10"])
        self.assertEqual(pygb._tokenizeCommandStr(" g +10 , +10 "), ["g", "+10", "+10"])
        self.assertEqual(pygb._tokenizeCommandStr("  g  +10  ,  +10  "), ["g", "+10", "+10"])

        self.assertEqual(pygb._tokenizeCommandStr("g-10,-10"), ["g", "-10", "-10"])
        self.assertEqual(pygb._tokenizeCommandStr("g -10,-10"), ["g", "-10", "-10"])
        self.assertEqual(pygb._tokenizeCommandStr("g-10 ,-10"), ["g", "-10", "-10"])
        self.assertEqual(pygb._tokenizeCommandStr("g-10, -10"), ["g", "-10", "-10"])
        self.assertEqual(pygb._tokenizeCommandStr(" g -10 , -10 "), ["g", "-10", "-10"])
        self.assertEqual(pygb._tokenizeCommandStr("  g  -10  ,  -10  "), ["g", "-10", "-10"])

        self.assertEqual(pygb._tokenizeCommandStr("d10,10"), ["d", "10", "10"])

        self.assertEqual(pygb._tokenizeCommandStr("d1,2g3,4"), ["d", "1", "2", "g", "3", "4"])

        self.assertEqual(pygb._tokenizeCommandStr("w'hello'"), ["w", "hello"])

        self.assertEqual(
            pygb._tokenizeCommandStr("d1,2w'hello'g3,4"), ["d", "1", "2", "w", "hello", "g", "3", "4"]
        )

        self.assertEqual(pygb._tokenizeCommandStr("s42"), ["s", "42"])
        self.assertEqual(pygb._tokenizeCommandStr("s42.3"), ["s", "42.3"])

        self.assertEqual(pygb._tokenizeCommandStr("f10(c)"), ["f", "10", ["c"]])
        self.assertEqual(pygb._tokenizeCommandStr("f10(lmr)"), ["f", "10", ["l", "m", "r"]])
        self.assertEqual(pygb._tokenizeCommandStr("f10(f5(cc))"), ["f", "10", ["f", "5", ["c", "c"]]])

        # TODO add negative cases

        # TODO add mocks for pygb for this.


class TypewriteThread(threading.Thread):
    def __init__(self, msg, interval=0.0):
        super(TypewriteThread, self).__init__()
        self.msg = msg
        self.interval = interval

    def run(self):
        time.sleep(0.25)  # NOTE: BE SURE TO ACCOUNT FOR THIS QUARTER SECOND FOR TIMING TESTS!
        pygb.typewrite(self.msg, self.interval)


class PressThread(threading.Thread):
    def __init__(self, keysArg):
        super(PressThread, self).__init__()
        self.keysArg = keysArg

    def run(self):
        time.sleep(0.25)  # NOTE: BE SURE TO ACCOUNT FOR THIS QUARTER SECOND FOR TIMING TESTS!
        pygb.press(self.keysArg)


class HoldThread(threading.Thread):
    def __init__(self, holdKeysArg, pressKeysArg=None):
        super(HoldThread, self).__init__()
        self.holdKeysArg = holdKeysArg
        self.pressKeysArg = pressKeysArg


    def run(self):
        time.sleep(0.25)  # NOTE: BE SURE TO ACCOUNT FOR THIS QUARTER SECOND FOR TIMING TESTS!
        with pygb.hold(self.holdKeysArg):
            if self.pressKeysArg is not None:
                pygb.press(self.pressKeysArg)
            else:
                pass


class TestKeyboard(unittest.TestCase):
    # NOTE: The terminal window running this script must be in focus during the keyboard tests.
    # You cannot run this as a scheduled task or remotely.

    def setUp(self):
        self.oldFailsafeSetting = pygb.FAILSAFE
        pygb.FAILSAFE = False
        pygb.moveTo(42, 42)  # make sure failsafe isn't triggered during this test
        pygb.FAILSAFE = True

    def tearDown(self):
        pygb.FAILSAFE = self.oldFailsafeSetting

    def test_typewrite(self):
        # 'Hello world!\n' test
        t = TypewriteThread("Hello world!\n")
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "Hello world!")

        # 'Hello world!\n' as a list argument
        t = TypewriteThread(list("Hello world!\n"))
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "Hello world!")

        # All printable ASCII characters test
        allKeys = []
        for c in range(32, 127):
            allKeys.append(chr(c))
        allKeys = "".join(allKeys)

        t = TypewriteThread(allKeys + "\n")
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, allKeys)

    def checkForValidCharacters(self, msg):
        for c in msg:
            self.assertTrue(pygb.isValidKey(c), '"%c" is not a valid key on platform %s' % (c, sys.platform))

    def test_typewrite_slow(self):

        # Test out the interval parameter to make sure it adds pauses.
        t = TypewriteThread("Hello world!\n", 0.1)
        startTime = time.time()
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "Hello world!")
        elapsed = time.time() - startTime
        self.assertTrue(1.0 < elapsed < 2.0, "Took %s seconds, expected 1.0 < x 2.0 seconds." % (elapsed))

    def test_typewrite_editable(self):
        # Backspace test
        t = TypewriteThread(["a", "b", "c", "\b", "backspace", "x", "y", "z", "\n"])
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "axyz")

        # TODO - Currently the arrow keys don't seem to work entirely correctly on OS X.
        if sys.platform != "darwin":
            # Arrow key test
            t = TypewriteThread(["a", "b", "c", "left", "left", "right", "x", "\n"])
            t.start()
            response = INPUT_FUNC()
            self.assertEqual(response, "abxc")

        # Del key test
        t = TypewriteThread(["a", "b", "c", "left", "left", "left", "del", "delete", "\n"])
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "c")

        # Home and end key test
        t = TypewriteThread(["a", "b", "c", "home", "x", "end", "z", "\n"])
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "xabcz")

    def test_press(self):
        # '' test
        t = PressThread("enter")
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "")

        # 'a' test, also test sending list of 1- and multi-length strings
        t = PressThread(["a", "enter"])
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "a")

        # 'ba' test, also test sending list of 1- and multi-length strings
        t = PressThread(["a", "left", "b", "enter"])
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "ba")

    def test_hold(self):
        # '' test
        t = HoldThread("enter")
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "")

        # 'a' test, also test sending list of 1- and multi-length strings
        t = HoldThread(["a", "enter"])
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "a")

        # 'ba' test, also test sending list of 1- and multi-length strings
        t = HoldThread(["a", "left", "b", "enter"])
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "ba")

    def test_press_during_hold(self):
        # '' test
        t = HoldThread("shift", "enter")
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "")

        # 'a' test, also test sending list of 1- and multi-length strings
        t = HoldThread("shift", ["a", "enter"])
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "A")

        # 'ab' test, also test sending list of 1- and multi-length strings
        t = HoldThread("shift", ["a", "b", "enter"])
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "AB")

    def test_typewrite_space(self):
        # Backspace test
        t = TypewriteThread(["space", " ", "\n"])  # test both 'space' and ' '
        t.start()
        response = INPUT_FUNC()
        self.assertEqual(response, "  ")

    def test_isShiftCharacter(self):
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + '~!@#$%^&*()_+{}|:"<>?':
            self.assertTrue(pygb.isShiftCharacter(char))
        for char in "abcdefghijklmnopqrstuvwxyz" + " `1234567890-=,./;'[]\\":
            self.assertFalse(pygb.isShiftCharacter(char))


class TestFailSafe(unittest.TestCase):
    def test_failsafe(self):
        self.oldFailsafeSetting = pygb.FAILSAFE

        pygb.moveTo(1, 1)  # make sure mouse is not in failsafe position to begin with
        for x, y in pygb.FAILSAFE_POINTS:
            pygb.FAILSAFE = True
            # When move(), moveTo(), drag(), or dragTo() moves the mouse to a
            # failsafe point, it shouldn't raise the fail safe. (This would
            # be annoying. Only a human moving the mouse to a failsafe point
            # should trigger the failsafe.)
            pygb.moveTo(x, y)

            pygb.FAILSAFE = False
            pygb.moveTo(1, 1)  # make sure mouse is not in failsafe position to begin with (for the next iteration)

        pygb.moveTo(1, 1)  # make sure mouse is not in failsafe position to begin with
        for x, y in pygb.FAILSAFE_POINTS:
            pygb.FAILSAFE = True
            pygb.moveTo(x, y)  # This line should not cause the fail safe exception to be raised.

            # A second pygb function call to do something while the cursor is in a fail safe point SHOULD raise the failsafe:
            self.assertRaises(pygb.FailSafeException, pygb.press, "esc")

            pygb.FAILSAFE = False
            pygb.moveTo(1, 1)  # make sure mouse is not in failsafe position to begin with (for the next iteration)

        for x, y in pygb.FAILSAFE_POINTS:
            pygb.FAILSAFE = False
            pygb.moveTo(x, y)  # This line should not cause the fail safe exception to be raised.

            # This line shouldn't cause a failsafe to trigger because FAILSAFE is set to False.
            pygb.press("esc")

        pygb.FAILSAFE = self.oldFailsafeSetting


class TestPyScreezeFunctions(unittest.TestCase):
    def test_locateFunctions(self):
        # TODO - for now, we only test that the "return None" and "raise pygb.ImageNotFoundException" is raised.

        pygb.useImageNotFoundException()
        with self.assertRaises(pygb.ImageNotFoundException):
            pygb.locate("100x100blueimage.png", "100x100redimage.png")
        # Commenting out the locateAll*() functions because they return generators, even if the image can't be found. Should they instead raise an exception? This is a question for pyscreeze's design.
        # with self.assertRaises(pygb.ImageNotFoundException):
        #    pygb.locateAll('100x100blueimage.png', '100x100redimage.png')

        # with self.assertRaises(pygb.ImageNotFoundException):
        #    pygb.locateAllOnScreen('100x100blueimage.png') # NOTE: This test fails if there is a blue square visible on the screen.
        with self.assertRaises(pygb.ImageNotFoundException):
            pygb.locateOnScreen(
                "100x100blueimage.png"
            )  # NOTE: This test fails if there is a blue square visible on the screen.
        with self.assertRaises(pygb.ImageNotFoundException):
            pygb.locateCenterOnScreen(
                "100x100blueimage.png"
            )  # NOTE: This test fails if there is a blue square visible on the screen.

        pygb.useImageNotFoundException(False)
        self.assertEqual(pygb.locate("100x100blueimage.png", "100x100redimage.png"), None)
        # self.assertEqual(pygb.locateAll('100x100blueimage.png', '100x100redimage.png'), None)
        # self.assertEqual(pygb.locateAllOnScreen('100x100blueimage.png'), None) # NOTE: This test fails if there is a blue square visible on the screen.
        self.assertEqual(
            pygb.locateOnScreen("100x100blueimage.png"), None
        )  # NOTE: This test fails if there is a blue square visible on the screen.
        self.assertEqual(
            pygb.locateCenterOnScreen("100x100blueimage.png"), None
        )  # NOTE: This test fails if there is a blue square visible on the screen.


if __name__ == "__main__":
    unittest.main()
