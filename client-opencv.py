import cv2
import argparse
from datetime import datetime, timedelta
from time import sleep

from multiprocessing.connection import Client


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--host', type=str, default='localhost', help='name or IP of the host that process the images')
    parser.add_argument('--port', type=int, default=5000, help='image processor server TCP port')
    parser.add_argument('--slow-fps', type=int, default=1, help='default FPS')
    parser.add_argument('--fast-fps', type=int, default=20, help='FPS when event is detected')
    parser.add_argument('--frame-width', type=int, default=480, help='frame width')
    parser.add_argument('--frame-height', type=int, default=360, help='frame height')
    parser.add_argument('--show', type=bool, default=True, help='show frame')
    parser.add_argument('--detect', nargs='+', type=str, default=['person'], help='what to detect.')
    parser.add_argument('--threshold', type=float, default=0.51, help='what to detect.')
    args = parser.parse_args()

    slow_fps = args.slow_fps
    fast_fps = args.fast_fps
    if slow_fps <= 0:
        slow_fps = 1
    if fast_fps < slow_fps:
        fast_fps = slow_fps
    interval = timedelta(0, slow_fps)

    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, args.frame_width)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, args.frame_height)

    dest = (args.host, args.port)
    conn = Client(dest)

    print("Starting capture. Press <q> to Quit.")
    frame_id = 0
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
            if len(detected) > 0 and max(detected.values()) > args.threshold:
                print("detected: %s" % str(detected))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_id += 1
        time_to_sleep = (t0 + interval - datetime.now()).total_seconds()
        if time_to_sleep > 0:
            sleep(time_to_sleep)

    conn.close()
