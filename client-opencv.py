import cv2
import argparse
from datetime import datetime, timedelta
from time import sleep

from multiprocessing.connection import Client
import logging as logger


def get_log_level(level):
    levels = {'CRITICAL': 50,
              'ERROR': 40,
              'WARNING': 30,
              'INFO': 20,
              'DEBUG': 10,
              'NOTSET': 0,
              }
    level = level.upper()
    return levels[level] if level in levels else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--host', type=str, default='localhost', help='name or IP of the host that process the images')
    parser.add_argument('--port', type=int, default=5000, help='image processor server TCP port')
    parser.add_argument('--low-fps', type=int, default=2, help='default FPS')
    parser.add_argument('--high-fps', type=int, default=20, help='FPS when event is detected')
    parser.add_argument('--high-period', type=int, default=30, help='high res period (in seconds)')
    parser.add_argument('--frame-width', type=int, default=480, help='frame width')
    parser.add_argument('--frame-height', type=int, default=360, help='frame height')
    parser.add_argument('--show', type=bool, default=True, help='show frame')
    parser.add_argument('--detect', nargs='+', type=str, default=['person'], help='what to detect.')
    parser.add_argument('--threshold', type=float, default=0.51, help='what to detect.')
    parser.add_argument('--log-level', type=str, default="INFO", help='log level.')
    parser.add_argument('--dir', type=str, default="images", help='detected images by trigger')
    args = parser.parse_args()

    FORMAT = '%(asctime)-15s %(message)s'
    logger.basicConfig(format=FORMAT)
    log = logger.getLogger('opencv-client')
    log.setLevel(get_log_level(args.log_level))

    import os
    if not os.path.exists(args.dir):
        os.mkdir(args.dir)
    FILENAME_FORMAT = os.path.join(args.dir, 'capture%s.jpg')

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

    log.info("Starting capture - fps %d. Press <q> to Quit." % slow_fps)
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
        if 'frame' in recv_data:
            image = recv_data['frame']
        if args.show:
            cv2.imshow('VideoCapture', image)
        if 'detected' in recv_data:
            detected = recv_data['detected']
            if len(detected) > 0 and max(detected.values()) > args.threshold:
                log.debug("detected: %s" % str(detected))
                if thigh is None:
                    log.info('in high speed - fps %d - frame_id %d' % (fast_fps, frame_id))
                    filename = FILENAME_FORMAT % t0.strftime('%Y-%m-%dT%H-%M-%S')
                    cv2.imwrite(filename, image)
                thigh = t0  # start high frame period
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_id += 1
        if thigh is not None:
            if (thigh + period_highres) < datetime.now():
                slow = True
                thigh = None
                log.info('returning to low speed - frame_id %d' % frame_id)
            else:
                slow = False
        if slow:
            time_to_sleep = (t0 + interval_lowres - datetime.now()).total_seconds()
        else:
            time_to_sleep = (t0 + interval_highres - datetime.now()).total_seconds()
        if time_to_sleep > 0:
            sleep(time_to_sleep)

    conn.close()
