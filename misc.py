import cv2
import sys
# from termios import tcflush, TCIFLUSH
import pickle
import copy

def convert_bb_from_xy12(rect, confidence='Unknown'):
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
    w = r - l
    h = b - t
    bb_dict = {'rect':{ 'l':l, 't':t, 'b':b, 'r':r, 'w':w, 'h':h },
                'confidence': confidence}
    return bb_dict

def convert_bb_from_cv(bb, confidence='Unknown'):
    bb_dict = {'rect':{ 'l': bb[0],
                        't': bb[1],
                        'w': bb[2],
                        'h': bb[3]},
                'confidence': confidence}
    bb_dict['rect']['r'] = bb_dict['rect']['l'] + bb_dict['rect']['w'] 
    bb_dict['rect']['b'] = bb_dict['rect']['t'] + bb_dict['rect']['h'] 
    return bb_dict

def convert_bb_to_cv(bb):
    return (int(bb['rect']['l']), 
            int(bb['rect']['t']), 
            int(bb['rect']['w']), 
            int(bb['rect']['h']))

# def fresh_input(qn):
#     tcflush(sys.stdin, TCIFLUSH)
#     chosen = input(qn)
#     return chosen

def init_imshow(name, loc=[0,0], win_size=[1600,900]):
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(name, *win_size)
    cv2.moveWindow(name, *loc)

def show(name, frame):
# def show(name, frame, loc=[0,0]):
    # cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    # cv2.namedWindow(name, cv2.WND_PROP_FULLSCREEN)
    # cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # cv2.resizeWindow(name, *win_size)
    # cv2.moveWindow(name, *loc)
    cv2.imshow(name, frame)
    cv2.waitKey(1)

def strict_waitKey(accepted):
    key = cv2.waitKey(0) & 0xFF
    while key not in accepted:
        key = cv2.waitKey(0) & 0xFF
    return key

class ASCII:
    BACKSPACE = 8
    ENTER = 13
    ESC = 27
    SPACE = 32

def persist_print(text):
    sys.stdout.write("\r{}     ".format(text))
    sys.stdout.flush()

def walk_forth(frame_count, total_frames):
    frame_count += 1
    if frame_count >= total_frames - 1:
        frame_count = total_frames - 1
        persist_print('Reached last. Frame {}/{}'.format(frame_count+1, total_frames))
    else:
        persist_print('Going forward. Frame {}/{}'.format(frame_count+1, total_frames))
    return frame_count

def walk_back(frame_count, total_frames):
    frame_count -= 1
    if frame_count <= 0:
        frame_count = 0
        persist_print('First frame. Frame {}/{}'.format(frame_count+1, total_frames))
    else:
        persist_print('Going back. Frame {}/{}'.format(frame_count+1, total_frames))
    return frame_count

def run_forth(frame_count, total_frames):
    frame_count += 5
    if frame_count >= total_frames - 1:
        frame_count = total_frames - 1
        persist_print('Reached last. Frame {}/{}'.format(frame_count+1, total_frames))
    else:
        persist_print('Running forward. Frame {}/{}'.format(frame_count+1, total_frames))
    return frame_count

def run_back(frame_count, total_frames):
    frame_count -= 5
    if frame_count <= 0:
        frame_count = 0
        persist_print('First frame. Frame {}/{}'.format(frame_count+1, total_frames))
    else:
        persist_print('Running back. Frame {}/{}'.format(frame_count+1, total_frames))
    return frame_count

def cash_out_face(annotations, current_frame, classes, annot_out_pickle):
    print('Saving current annotations..')
    # print(annotations)
    # print(current_frame)
    with open(annot_out_pickle,'wb') as pf:
        pickle.dump((annotations,current_frame,classes), pf)
        print('Saved current annotations to {}!'.format(annot_out_pickle))

def end_track_face(annotations, frame_count, classes, annot_out_pickle, in_tracking, state, resizer):
    print('\nEnded Track of {}'.format(in_tracking))
    cash_out_face(annotations, frame_count, classes, annot_out_pickle)
    in_tracking = None
    # state = State.FIND
    state.set_state('FIND')
    resizer.reset()
    return in_tracking

def cash_out(annotations, current_frame, classes, trk_idx, annot_out_pickle):
    print('Saving current annotations..')
    # print(annotations)
    # print(current_frame)
    with open(annot_out_pickle,'wb') as pf:
        pickle.dump((annotations,current_frame,classes,trk_idx), pf)
        print('Saved current annotations to {}!'.format(annot_out_pickle))

def end_track(annotations, frame_count, classes, trk_idx, annot_out_pickle, in_tracking, state, resizer):
    print('\nEnded Track of {}'.format(in_tracking))
    cash_out(annotations, frame_count, classes, trk_idx, annot_out_pickle)
    in_tracking = None
    # state = State.FIND
    state.set_state('FIND')
    resizer.reset()
    return in_tracking

def clip_within(bb, frame):
    clipped = False
    h, w = frame.shape[:2]
    if bb['rect']['r'] > w-1:
        bb['rect']['r'] = w-1
        clipped = True
    if bb['rect']['l'] > w-1:
        bb['rect']['l'] = w-1
        clipped = True
    if bb['rect']['r'] < 0:
        bb['rect']['l'] = 0
        clipped = True
    if bb['rect']['l'] < 0:
        bb['rect']['l'] = 0
        clipped = True

    if bb['rect']['t'] < 0:
        bb['rect']['t'] = 0
        clipped = True
    if bb['rect']['b'] < 0:
        bb['rect']['b'] = 0
        clipped = True
    if bb['rect']['t'] > h-1:
        bb['rect']['t'] = h-1
        clipped = True
    if bb['rect']['b'] > h-1:
        bb['rect']['b'] = h-1
        clipped = True

    if clipped:
        bb['rect']['w'] = bb['rect']['r'] - bb['rect']['l'] + 1
        if bb['rect']['w'] <= 0:
            return False, None
        bb['rect']['h'] = bb['rect']['b'] - bb['rect']['t'] + 1
        if bb['rect']['h'] <= 0:
            return False, None

    return True, bb

def normmylise(raw_bb, width, height):
    norm_bb = copy.deepcopy(raw_bb)
    norm_bb['rect']['l'] = raw_bb['rect']['l'] / width
    norm_bb['rect']['r'] = raw_bb['rect']['r'] / width
    norm_bb['rect']['w'] = raw_bb['rect']['w'] / width
    norm_bb['rect']['t'] = raw_bb['rect']['t'] / height
    norm_bb['rect']['b'] = raw_bb['rect']['b'] / height
    norm_bb['rect']['h'] = raw_bb['rect']['h'] / height
    return norm_bb

def unnormmylise(norm_bb, width, height):
    raw_bb = copy.deepcopy(norm_bb)
    raw_bb['rect']['l'] = int(norm_bb['rect']['l'] * width)
    raw_bb['rect']['r'] = int(norm_bb['rect']['r'] * width)
    raw_bb['rect']['w'] = raw_bb['rect']['r'] - raw_bb['rect']['l'] + 1
    raw_bb['rect']['t'] = int(norm_bb['rect']['t'] * height)
    raw_bb['rect']['b'] = int(norm_bb['rect']['b'] * height)
    raw_bb['rect']['h'] = raw_bb['rect']['b'] -  raw_bb['rect']['t'] + 1 
    return raw_bb