import cv2

def window_is_open(window_name, delay=1):
    return (
        cv2.waitKey(delay) == -1  # No keys pressed
        and
        cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) == 1.0 # window not closed
    )
