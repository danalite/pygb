# [ Imports ]
import Quartz
import AppKit


# [ API ]
def click(x, y, window_id, pid):
    """Click at x, y in the app with the pid."""
    point = Quartz.CGPoint()
    point.x = x
    point.y = y

    event_types = (
        AppKit.NSEventTypeMouseMoved,
        AppKit.NSEventTypeLeftMouseDown,
        AppKit.NSEventTypeLeftMouseUp,
    )

    for this_event_type in event_types:
        event = _create_ns_mouse_event(this_event_type, point=point, window_id=window_id)
        Quartz.CGEventPostToPid(pid, event)


# [ Internal ]
def _create_ns_mouse_event(event_type, point, window_id=None):
    """Create a mouse event."""
    print(event_type, point, window_id)
    create_ns_mouse_event = AppKit.NSEvent.mouseEventWithType_location_modifierFlags_timestamp_windowNumber_context_eventNumber_clickCount_pressure_
    ns_event = create_ns_mouse_event(
        event_type,  # Event type
        point,  # Window-specific coordinate
        0,  # Flags
        AppKit.NSProcessInfo.processInfo().systemUptime(),  # time of the event since system boot
        window_id,  # window ID the event is targeted to
        None,  # display graphics context.
        0,  # event number
        1,  # the number of mouse clicks associated with the event.
        0  # pressure applied to the input device, from 0.0 to 1.0
    )
    return ns_event.CGEvent()


# [ Script ]
if __name__ == "__main__":
    click(240, 25, 525, 3253)