import argparse
from multiprocessing.connection import Listener
from multiprocessing import Queue, Pool
import tensorflow as tf

from frozen_detection_graph import PATH_TO_CKPT
from images import detect_objects
from images import category_idx


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
            data_to_process = {'conn': conn, 'data': data}
            input_q.put(data_to_process)
        except Exception:
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--host', type=str, default='localhost', help='name or IP of the host that process the images')
    parser.add_argument('--port', type=int, default=5000, help='image processor server TCP port')
    parser.add_argument('--queue-size', type=int, default=5, help='Size of the queue.')
    parser.add_argument('--num-workers', type=int, default=2, help='Number of workers.')
    parser.add_argument('--detect', nargs='+', type=str, default=['person'], help='what to detect.')
    args = parser.parse_args()

    """what must be detected"""
    categories_to_detect = []
    for w in args.detect:
        categories_to_detect.append(category_idx(w))

    address = ('localhost', args.port)  # bind all addresses
    listener = Listener(address)  # , authkey='secret password')

    input_q = Queue(maxsize=args.queue_size)
    pool = Pool(args.num_workers, worker, (input_q, categories_to_detect))

    print('binding completed @ port %d' % args.port)
    print('detecting: %s' % " ".join(args.detect))
    while True:
        conn = listener.accept()
        client_address = listener.last_accepted  # client address
        print('station %s connected' % client_address[0])
        process_connections(input_q, conn, client_address)
    listener.close()
