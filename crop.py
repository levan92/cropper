import cv2
import copy 
if __name__ == '__main__':
    from misc import init_imshow, show
else:   
    from .misc import init_imshow, show

mouse_pt = None
click_pt = None
start_click_pt = None
stored_rect_pts = None
pre_adjust_mode = []
adjust_mode = []
move_start_pt = None
anchor_rect_pts = None

edge_buffer = 6
edge_x = -1
edge_y = -1
buff = 10 #line buffer

def mouse_events_handler(event, x, y, flags, param):
    global mouse_pt, click_pt, edge_x, edge_y
    if (0 - edge_buffer) <= x <= (0 + edge_buffer):
        x = 0
        # x = -1
        edge_x = 0
    elif (frame_size[1]-1 - edge_buffer) <= x <= (frame_size[1]-1 + edge_buffer):
        x = frame_size[1] - 1   
        # x = frame_size[1] - 2   
        edge_x = frame_size[1] - 1
    else:
        edge_x = -1
    if (0 - edge_buffer) <= y <= (0 + edge_buffer):
        y = 0
        # y = -1
        edge_y = 0
    elif (frame_size[0]-1 - edge_buffer) <= y <= (frame_size[0]-1 + edge_buffer):
        y = frame_size[0]-1
        # y = frame_size[0]-2
        edge_y = frame_size[0]-1
    else:
        edge_y = -1

    if event == cv2.EVENT_MOUSEMOVE:
        mouse_pt = (x,y)
    if event == cv2.EVENT_LBUTTONDOWN:
        click_pt = (x,y)
        # print(click_pt)
    # print('frame size:', frame_size)
        # print('Click! {}'.format(click_pt))

def edge_drawing(frame):
    colour = (50,50,255)
    THICC = edge_buffer + 1
    if edge_x >= 0:
        cv2.line(frame, (edge_x,0), (edge_x, frame_size[0]-1), colour, THICC)
    if edge_y >= 0:
        cv2.line(frame, (0, edge_y), (frame_size[1]-1, edge_y), colour, THICC)
    return frame

def draw_crosshair(frame):
    global mouse_pt
    if mouse_pt:
        colour = (0,255,0)
        THICC = 2
        frameDC = copy.deepcopy(frame)
        h, w = frameDC.shape[:2]
        vertical_start = (mouse_pt[0], 0) 
        vertical_end = (mouse_pt[0], h-1)
        horizontal_start = (0, mouse_pt[1]) 
        horizontal_end = (w-1, mouse_pt[1]) 
        # print('vertical:',vertical_start, vertical_end)
        # print('horizontal:', horizontal_start, horizontal_end)
        cv2.line(frameDC, vertical_start, vertical_end, colour, THICC)
        cv2.line(frameDC, horizontal_start, horizontal_end, colour, THICC)
        return frameDC
    else:
        return frame

def check_adjust_multi(frame):
    global pre_adjust_mode, mouse_pt, click_pt, multi_stored_rect_pts
    if mouse_pt and multi_stored_rect_pts and not click_pt and not start_click_pt:
        for i, bb in enumerate(multi_stored_rect_pts):
            if bb is None:
                continue
            rect_xmin = bb[0][0]
            rect_ymin = bb[0][1]
            rect_xmax = bb[1][0]
            rect_ymax = bb[1][1]
            colour = (0,0,255)
            THICCC = 6
            buff = 6
            pre_adjust_mode = []
            if (rect_xmin + buff < mouse_pt[0] < rect_xmax - buff ) and (rect_ymin + buff < mouse_pt[1] < rect_ymax - buff ):
                cv2.line(frame, (rect_xmin, rect_ymin), (rect_xmax, rect_ymin), colour, THICCC)
                cv2.line(frame, (rect_xmin, rect_ymax), (rect_xmax, rect_ymax), colour, THICCC)
                cv2.line(frame, (rect_xmin, rect_ymin), (rect_xmin, rect_ymax), colour, THICCC)
                cv2.line(frame, (rect_xmax, rect_ymin), (rect_xmax, rect_ymax), colour, THICCC)
                if not pre_adjust_mode:
                    pre_adjust_mode.append(i)
                pre_adjust_mode.append('move')
            else:
                if (rect_xmin <= mouse_pt[0] <= rect_xmax) and (rect_ymin - buff) <= mouse_pt[1] <= (rect_ymin + buff):
                    cv2.line(frame, (rect_xmin, rect_ymin), (rect_xmax, rect_ymin), colour, THICCC)
                    if not pre_adjust_mode:
                        pre_adjust_mode.append(i)
                    pre_adjust_mode.append('top')
                if (rect_xmin <= mouse_pt[0] <= rect_xmax) and (rect_ymax - buff) <= mouse_pt[1] <= (rect_ymax + buff):
                    cv2.line(frame, (rect_xmin, rect_ymax), (rect_xmax, rect_ymax), colour, THICCC)
                    if not pre_adjust_mode:
                        pre_adjust_mode.append(i)
                    pre_adjust_mode.append('bot')
                if (rect_ymin <= mouse_pt[1] <= rect_ymax) and (rect_xmin - buff) <= mouse_pt[0] <= (rect_xmin + buff):
                    cv2.line(frame, (rect_xmin, rect_ymin), (rect_xmin, rect_ymax), colour, THICCC)
                    if not pre_adjust_mode:
                        pre_adjust_mode.append(i)
                    pre_adjust_mode.append('left')
                if (rect_ymin <= mouse_pt[1] <= rect_ymax) and (rect_xmax - buff) <= mouse_pt[0] <= (rect_xmax + buff):
                    cv2.line(frame, (rect_xmax, rect_ymin), (rect_xmax, rect_ymax), colour, THICCC)
                    if not pre_adjust_mode:
                        pre_adjust_mode.append(i)
                    pre_adjust_mode.append('right')

            if pre_adjust_mode:
                break

def process_rect(pt1, pt2):
    xmin = min(pt1[0], pt2[0])
    xmax = max(pt1[0], pt2[0])
    ymin = min(pt1[1], pt2[1])
    ymax = max(pt1[1], pt2[1])
    return [[xmin, ymin], [xmax, ymax]]

def adjust_rect():
    global mouse_pt, adjust_mode
    temp_stored_rect_pts = [[None, None], [None, None]]
    try:
        if mouse_pt is not None:
            if 'left' in adjust_mode:
                temp_stored_rect_pts[0][0] = mouse_pt[0]
            if 'right' in adjust_mode:
                temp_stored_rect_pts[1][0] = mouse_pt[0]
            if 'top' in adjust_mode:
                temp_stored_rect_pts[0][1] = mouse_pt[1]
            if 'bot' in adjust_mode:
                temp_stored_rect_pts[1][1] = mouse_pt[1]
    except Exception as e:
        print('Exception occured: {}'.format(e))
        return False, None
    return True, temp_stored_rect_pts

def move_rect(anchor_rect_pts):
    global mouse_pt
    temp_stored_rect_pts = [[None, None], [None, None]]
    if mouse_pt is not None:
        diff_x = mouse_pt[0] - move_start_pt[0]
        diff_y = mouse_pt[1] - move_start_pt[1]
        temp_stored_rect_pts[0][0] = anchor_rect_pts[0][0] + diff_x
        temp_stored_rect_pts[0][1] = anchor_rect_pts[0][1] + diff_y
        temp_stored_rect_pts[1][0] = anchor_rect_pts[1][0] + diff_x
        temp_stored_rect_pts[1][1] = anchor_rect_pts[1][1] + diff_y
    return True, temp_stored_rect_pts

def update(old, new):
    for i, corner in enumerate(new):
        for j, value in enumerate(corner):
            if value:
                old[i][j] = value
                # print(i,j,value)
    return old

## only for edit mode
def process_multi(frame, single_mode):
    global start_click_pt, click_pt, multi_stored_rect_pts, pre_adjust_mode, adjust_mode, confs, move_start_pt, anchor_rect_pts
    if pre_adjust_mode and not adjust_mode and not start_click_pt and click_pt:
        # print('[Drawer] Adjust mode on')
        if 'move' in pre_adjust_mode:
            move_start_pt = click_pt
            anchor_rect_pts = copy.deepcopy(multi_stored_rect_pts[pre_adjust_mode[0]])
        adjust_mode = pre_adjust_mode
        pre_adjust_mode = []
        click_pt = None
    elif adjust_mode and move_start_pt is None and mouse_pt is not None and not click_pt:
        # print('[Drawer] Adjusting')
        ret, temp_stored_rect_pts = adjust_rect()
        if ret:
            multi_stored_rect_pts[adjust_mode[0]] = update(multi_stored_rect_pts[adjust_mode[0]], temp_stored_rect_pts)
    elif adjust_mode and move_start_pt is not None and mouse_pt is not None and not click_pt:
        # print('[Drawer] Moving')
        ret, temp_stored_rect_pts = move_rect(anchor_rect_pts)
        if ret:
            multi_stored_rect_pts[adjust_mode[0]] = update(multi_stored_rect_pts[adjust_mode[0]], temp_stored_rect_pts)
    elif adjust_mode or (single_mode and start_click_pt and click_pt):
        # stored_rect_pts = process_rect(*stored_rect_pts)
        if adjust_mode:
            multi_stored_rect_pts[adjust_mode[0]] = process_rect(*multi_stored_rect_pts[adjust_mode[0]])
            confs[adjust_mode[0]] = 'User-drawn'
        else:
            multi_stored_rect_pts[0] = process_rect(start_click_pt, click_pt)
            confs[0] = 'User-drawn'
        adjust_mode = []
        move_start_pt = None
        click_pt = None
        start_click_pt = None
        # print('[Drawer] Adjust mode ended. New rect: {}'.format(stored_rect_pts))
    elif single_mode and click_pt and not start_click_pt:
        start_click_pt = click_pt
        click_pt = None
    elif single_mode and start_click_pt and mouse_pt and not click_pt:
        frameDC = copy.deepcopy(frame)
        colour = (0,0,255)
        THICC = 2
        cv2.rectangle(frameDC, start_click_pt, mouse_pt, colour, THICC)
        return frameDC
    else:
        click_pt = None
    return frame

# def draw_stored_rect(frame):
#     if stored_rect_pts and not start_click_pt:
#         frameDC = copy.deepcopy(frame)
#         colour = (200,200,0)
#         THICC = 2
#         cv2.rectangle(frameDC, tuple(stored_rect_pts[0]), tuple(stored_rect_pts[1]), colour, THICC)
#         return frameDC
#     return frame

def draw_stored_rect_multi(frame):
    frameDC = copy.deepcopy(frame)
    if multi_stored_rect_pts and not start_click_pt:
        colour = (200,200,0)
        THICC = 2
        for bb in multi_stored_rect_pts:
            if bb:
                cv2.rectangle(frameDC, tuple(bb[0]), tuple(bb[1]), colour, THICC)
    return frameDC

def pre_process(init_bb):
    bb = [[int(init_bb['rect']['l']), int(init_bb['rect']['t'])],
          [int(init_bb['rect']['r']), int(init_bb['rect']['b'])]]
    return bb, init_bb['confidence']

def pre_process_multi(init_bbs):
    bbs = []
    confs = []
    for init_bb in init_bbs:
        bb, conf = pre_process(init_bb)
        bbs.append(bb)
        confs.append(conf)
    return bbs, confs

def post_process(rect, confidence='Unknown'):
    '''
    rect: list of 2 tuples (x, y)
    '''
    # l = min(rect[0][0], rect[1][0])
    # t = min(rect[0][1], rect[1][1])
    # r = max(rect[0][0], rect[1][0])
    # b = max(rect[0][1], rect[1][1])
    l = rect[0][0]
    t = rect[0][1]
    r = rect[1][0]
    b = rect[1][1]
    w = r - l + 1
    h = b - t + 1
    bb_dict = {'rect':{ 'l':l, 't':t, 'b':b, 'r':r, 'w':w, 'h':h },
                'confidence': confidence}
    return bb_dict

def post_process_multi(bbs, confs):
    proc_bbs = []
    for i, bb in enumerate(bbs):
        proc_bbs.append(post_process(bb, confs[i]))
    return proc_bbs

def bb_drawer(frame, shower, init_bb=None):
    global mouse_pt, click_pt, start_click_pt, multi_stored_rect_pts, pre_adjust_mode, adjust_mode, confs, frame_size
    mouse_pt = None
    click_pt = None
    start_click_pt = None
    stored_rect_pts = None
    pre_adjust_mode = []
    adjust_mode = []
    window_name = 'Draw BB'
    conf = None
    frame_size = frame.shape[:2]
    multi_stored_rect_pts = [None]
    confs = [None]
    if init_bb:
        stored_rect_pts, conf = pre_process(init_bb)
        multi_stored_rect_pts[0] = stored_rect_pts
        confs[0] = conf
    shower.start(window_name)
    # cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    # cv2.resizeWindow(window_name, 1920, 1080)
    # cv2.moveWindow(window_name, *screen_loc)

    # cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_events_handler)
    while True:
        # click_pt = None
        # cv2.moveWindow(window_name, *screen_loc)
        frameSHOW = draw_crosshair(frame)
        frameSHOW = edge_drawing(frameSHOW)
        check_adjust_multi(frameSHOW)
        frameSHOW = process_multi(frameSHOW, single_mode = True)
        frameSHOW = draw_stored_rect_multi(frameSHOW)
        # show(window_name, frameSHOW)
        shower.show(window_name, frameSHOW, wait=-1)
        key = cv2.waitKey(1) & 0xFF
        if key == 13 or key==32: # Enter or Spacebar
            if not adjust_mode and not start_click_pt and multi_stored_rect_pts[0] is not None:
            # if not pre_adjust_mode and not adjust_mode and not start_click_pt and multi_stored_rect_pts[0] is not None:
                res = post_process_multi(multi_stored_rect_pts, confs)[0]
                break
        elif key == ord('c'):
            res = None
            break
    # mouse_pt = None
    # click_pt = None
    # start_click_pt = None
    # stored_rect_pts = None
    # cv2.destroyAllWindows()
    return res

def bbs_editor(frame, shower, bbs=[]):
    global mouse_pt, click_pt, start_click_pt, multi_stored_rect_pts, pre_adjust_mode, adjust_mode, confs, frame_size
    mouse_pt = None
    click_pt = None
    start_click_pt = None
    multi_stored_rect_pts = []
    pre_adjust_mode = []
    adjust_mode = []
    window_name = 'Edit BBs'
    frame_size = frame.shape[:2]
    multi_stored_rect_pts, confs = pre_process_multi(bbs)
    shower.start(window_name)
    # cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_events_handler)
    while True:
        # click_pt = None
        # cv2.moveWindow(window_name, *screen_loc)
        frameSHOW = draw_crosshair(frame)
        frameSHOW = edge_drawing(frameSHOW)
        check_adjust_multi(frameSHOW)
        frameSHOW = process_multi(frameSHOW, single_mode = False)
        frameSHOW = draw_stored_rect_multi(frameSHOW)
        # show(window_name, frameSHOW)
        shower.show(window_name, frameSHOW, wait=-1)
        key = cv2.waitKey(1) & 0xFF
        if key == 13 or key==32: # Enter or Spacebar
            if not pre_adjust_mode and not adjust_mode and not start_click_pt:
                res = post_process_multi(multi_stored_rect_pts, confs)
                print('Edit saved.')
                break
        elif key == ord('c'):
            res = bbs
            print('Edit cancelled.')
            break
    cv2.destroyAllWindows()
    return res

if __name__ == '__main__':
    import time
    from shower import Shower
    import sys
    import argparse
    import os

    parser = argparse.ArgumentParser()

    parser.add_argument('img',help='Image to crop')
    parser.add_argument('--out', help='output image path')

    args = parser.parse_args()
    assert os.path.exists(args.img),'Image given does not exist'

    if args.out is None:    
        out = args.img.split('.')[0] + '_crop.png'
    else:
        out = args.out

    # img_path =  '/home/dh/Workspace/REID/waldo_data/naruto2.jpg'
    shower = Shower()
    frame = cv2.imread(args.img)

    res = bb_drawer(frame, init_bb=None, shower=shower)
    if res:
        l = res['rect']['l']
        t = res['rect']['t']
        b = res['rect']['b']
        r = res['rect']['r']
        out_img = frame[ t:b, l:r ]
        cv2.imwrite(out, out_img)
