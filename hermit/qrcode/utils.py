import cv2


def window_is_open(window_name):
    return (cv2.waitKey(1) and
            cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) == 1.0)
