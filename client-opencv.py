import cv2
import argparse
from datetime import datetime, timedelta
from time import sleep

from multiprocessing.connection import Client


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--host', type=str, default='localhost', help='name or IP of the host that process the images')
    parser.add_argument('--port', type=int, default=5000, help='image processor server TCP port')
    parser.add_argument('--low-fps', type=int, default=2, help='default FPS')
    parser.add_argument('--high-fps', type=int, default=20, help='FPS when event is detected')
    parser.add_argument('--high-period', type=int, default=60, help='high res period (in seconds)')
    parser.add_argument('--frame-width', type=int, default=480, help='frame width')
    parser.add_argument('--frame-height', type=int, default=360, help='frame height')
    parser.add_argument('--show', type=bool, default=True, help='show frame')
    parser.add_argument('--detect', nargs='+', type=str, default=['person'], help='what to detect.')
    parser.add_argument('--threshold', type=float, default=0.51, help='what to detect.')
    args = parser.parse_args()

    slow_fps = args.low_fps
    fast_fps = args.high_fps
    if slow_fps <= 0:
        slow_fps = 1
    if fast_fps < slow_fps:
        fast_fps = slow_fps
    interval_lowres = timedelta(0, 1 / float(slow_fps))
    interval_highres = timedelta(0, 1 / float(fast_fps))
    period_highres = timedelta(0, args.high_period)

    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, args.frame_width)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, args.frame_height)

    dest = (args.host, args.port)
    conn = Client(dest)

    print("Starting capture - fps %d. Press <q> to Quit." % slow_fps)
    frame_id = 0
    slow = True
    thigh = None
    while True:
        t0 = datetime.now()
        _, frame = video_capture.read()
        # send message
        data = {'frame_id': frame_id, 'frame': frame}
        conn.send(data)
        # receive message (frame tagged) from server
        recv_data = conn.recv()
        # display image
        if args.show and 'frame' in recv_data:
            cv2.imshow('Video', recv_data['frame'])
        if 'detected' in recv_data:
            detected = recv_data['detected']
            print(frame_id, detected)
            if len(detected) > 0 and max(detected.values()) > args.threshold:
                print("detected: %s" % str(detected))
                if thigh is None:
                    print('in high speed - frame_id %d' % frame_id)
                thigh = t0  # start high frame period
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_id += 1
        if thigh is not None:
            if thigh + period_highres > datetime.now():
                slow = True
                thigh = None
                print('returning to low speed - frame_id %d' % frame_id)
            else:
                slow = False
        if slow:
            time_to_sleep = (t0 + interval_lowres - datetime.now()).total_seconds()
        else:
            time_to_sleep = (t0 + interval_highres - datetime.now()).total_seconds()
        if time_to_sleep > 0:
            sleep(time_to_sleep)

    conn.close()
