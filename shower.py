import cv2

class Shower(object):
    def __init__(self, win_size = [1600,900], win_loc = [0,0], min_size=[960,640]):
        self.win_size = win_size
        self.win_loc = win_loc
        self.min_size = min_size

    def start(self, name):
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        # cv2.resizeWindow(name, *self.win_size)
        cv2.moveWindow(name, *self.win_loc)

    def show(self, name, frame, wait=1):
        frame_h, frame_w = frame.shape[:2]
        w_scale = 1
        h_scale = 1
        if frame_w > self.win_size[0]:
            w_scale = self.win_size[0]/frame_w
        if frame_h > self.win_size[1]:
            h_scale = self.win_size[1]/frame_h
        # scale = 1
        scale = min(w_scale, h_scale)
        w = max( int(frame_w * scale), self.min_size[0] )
        h = max( int(frame_h * scale), self.min_size[1] )
        cv2.resizeWindow(name, w,h )
        cv2.imshow(name, frame)
        if wait >= 0:
            cv2.waitKey(wait)