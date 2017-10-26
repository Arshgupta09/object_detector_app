#
#
# to run this app, server-opencv.py must be running, otherwise you get a connection error
# run the following commands:
#
# $ cd object_detector_app
# $ source activate object-detection
# $ python3 client-opencv.py
#
import cv2
import argparse
from datetime import datetime, timedelta
# from time import sleep
from utils.app_utils import FPS
from utils.app_utils import WebcamVideoStream

from multiprocessing.connection import Client
from common_utils import get_log_level
import logging as logger

import pickle
import socket


def inform_ethanol(high, dest_ethanol):
    """this method sends a message to dest_ethanol to inform waht throughput is expected"""
    conn_ethanol = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn_ethanol.connect(dest_ethanol)
        obj = pickle.dumps(high, 0)
        conn_ethanol.send(obj)  # inform that high throughput is needed
        conn_ethanol.close()
        log.info('Send to ethanol @ %s:%d that throughput is %s' % (dest_ethanol[0], dest_ethanol[1], 'high' if high else 'low'))
    except ConnectionRefusedError:
        log.info("Server is not up")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('--host', type=str, default='192.168.1.100', help='name or IP of the host that process the images')
    parser.add_argument('--port', type=int, default=5000, help='image processor server TCP port')

    parser.add_argument('--host-ethanol', type=str, default='150.164.10.52', help='name or IP of the host that process the images')
    parser.add_argument('--port-ethanol', type=int, default=50000, help='image processor server TCP port')

    parser.add_argument('--low-fps', type=int, default=2, help='default FPS')
    parser.add_argument('--high-fps', type=int, default=20, help='FPS when event is detected')
    parser.add_argument('--high-period', type=int, default=30, help='high res period (in seconds) after a person is not detected anymore')

    parser.add_argument('-src', '--source', dest='video_source', type=int,
                        default=0, help='Device index of the camera.')
    parser.add_argument('--frame-width', type=int, default=240, help='frame width')  # 480
    parser.add_argument('--frame-height', type=int, default=180, help='frame height')  # 360

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

    # video_capture = cv2.VideoCapture(0)
    # video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, args.frame_width)
    # video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, args.frame_height)
    video_capture = WebcamVideoStream(src=args.video_source,
                                      width=args.frame_width,
                                      height=args.frame_height).start()

    dest = (args.host, args.port)
    dest_ethanol = (args.host_ethanol, args.port_ethanol)
    conn = Client(dest)

    log.info("Starting capture - fps %d. Press <q> to Quit." % slow_fps)

    frame_id = 0
    slow = True
    t_high = None

    fps = FPS().start()
    while True:
        t0 = datetime.now()
        frame = video_capture.read()
        # send message
        data = {'frame_id': frame_id, 'frame': frame}
        log.debug("Sending frame %d" % frame_id)
        conn.send(data)
        log.debug("Sent frame %d" % frame_id)
        # receive message (frame tagged) from server
        recv_data = conn.recv()
        log.debug("Received frame %d" % recv_data['frame_id'])
        fps.update()
        # display image
        if 'frame' in recv_data:
            image = recv_data['frame']
        if args.show:
            cv2.imshow('VideoCapture', image)
        if 'detected' in recv_data:
            detected = recv_data['detected']
            if len(detected) > 0 and max(detected.values()) > args.threshold:
                log.debug("detected: %s" % str(detected))
                if t_high is None:
                    log.info('in high speed - fps %d - frame_id %d' % (fast_fps, frame_id))
                    filename = FILENAME_FORMAT % t0.strftime('%Y-%m-%dT%H-%M-%S')
                    cv2.imwrite(filename, image)
                    # inform ethanol controller that a person was detected
                    inform_ethanol(True, dest_ethanol)
                t_high = t0  # start high frame period
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_id += 1
        if t_high is not None:
            if (t_high + period_highres) < datetime.now():
                slow = True
                t_high = None
                log.info('returning to low speed - frame_id %d' % frame_id)
                inform_ethanol(False, dest_ethanol)
            else:
                slow = False
        if slow:
            time_to_sleep = (t0 + interval_lowres - datetime.now()).total_seconds()
        else:
            time_to_sleep = (t0 + interval_highres - datetime.now()).total_seconds()
        # if time_to_sleep > 0:
        #     sleep(time_to_sleep)

    conn.close()
    fps.stop()
    print('[INFO] elapsed time (total): {:.2f}'.format(fps.elapsed()))
    print('[INFO] approx. FPS: {:.2f}'.format(fps.fps()))
