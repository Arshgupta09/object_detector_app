#
#
# to run this app:
#
# $ cd object_detector_app
# $ source activate object-detection
# $ python3 server-opencv.py
#
#
import argparse
from multiprocessing.connection import Listener
from multiprocessing import Queue, Pool
import tensorflow as tf

from frozen_detection_graph import PATH_TO_CKPT
from images import detect_objects
from images import category_idx

from common_utils import get_log_level
import logging as logger
FORMAT = '%(asctime)-15s %(message)s'
logger.basicConfig(format=FORMAT)
log = logger.getLogger('opencv-client')


def worker(input_q, categories_to_detect):
    # Load a (frozen) Tensorflow model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

        sess = tf.Session(graph=detection_graph)

    while True:
        data_to_process = input_q.get()
        frame = data_to_process['data']['frame']
        image, detected = detect_objects(frame, sess, detection_graph, categories_to_detect)
        result = data_to_process['data']
        result['frame'] = image
        result['detected'] = detected
        conn = data_to_process['conn']
        conn.send(result)
    sess.close()


def process_connections(input_q, conn, client_address):
    while True:
        try:
            data = conn.recv()
            log.debug("Received frame %d" % data['frame_id'] if 'frame_id' in data else -1)
            data_to_process = {'conn': conn, 'data': data}  # note: connection is in data_to_process
            input_q.put(data_to_process)
        except ValueError:
            log.info("ValueError detected - Probably you are not running the client or the server with python3")
            break
        except Exception:
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='name or IP of the host that process the images')
    parser.add_argument('--port', type=int, default=5000, help='image processor server TCP port')
    parser.add_argument('--queue-size', type=int, default=5, help='Size of the queue.')
    parser.add_argument('--num-workers', type=int, default=4, help='Number of workers.')
    parser.add_argument('--detect', nargs='+', type=str, default=['person'], help='what to detect.')
    parser.add_argument('--log-level', type=str, default="INFO", help='log level.')
    args = parser.parse_args()

    log.setLevel(get_log_level(args.log_level))

    """what must be detected"""
    categories_to_detect = []
    for w in args.detect:
        categories_to_detect.append(category_idx(w))

    address = (args.host, args.port)  # default bind all addresses
    listener = Listener(address)  # , authkey='secret password')

    input_q = Queue(maxsize=args.queue_size)
    pool = Pool(args.num_workers, worker, (input_q, categories_to_detect))

    log.info('binding completed @ port %d' % args.port)
    log.info('detecting: %s' % " ".join(args.detect))
    while True:
        conn = listener.accept()
        client_address = listener.last_accepted  # client address
        log.info('station %s connected' % client_address[0])
        process_connections(input_q, conn, client_address)
    listener.close()
