import cv2

def window_is_open(window_name, delay=1):
    # waitKey returns -1 if *no* keys were pressed during the delay.
    # If any key was pressed during the delay, it returns the code of
    # that key.
    #
    # As written, this variable is a boolean.
    no_keys_pressed_during_delay = cv2.waitKey(delay) == -1

    # On systems which support window properties (e.g. Qt backends
    # such as Linux) this is 0 or 1 (actually floats of those for some
    # damn reason).
    #
    # On a Mac, where window properties are not supported, this comes
    # out to -1.
    window_is_visible_value = cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE)
    window_is_visible = (window_is_visible_value != 0)

    return no_keys_pressed_during_delay and window_is_visible
