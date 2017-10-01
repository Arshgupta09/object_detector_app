import cv2
import multiprocessing
import time

import tensorflow as tf

from frozen_detection_graph import PATH_TO_CKPT
from images import detect_objects, blend_non_transparent


def main_process(input, output):
    while True:
        time.sleep(0.5)
        image = input.get()
        output.put(image)


def child_process(input, output):
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
        image = input.get()
        image2, detected = detect_objects(image, sess, detection_graph)
        result = blend_non_transparent(image, image2)
        output.put(result)


if __name__ == '__main__':
    input = multiprocessing.Queue(5)
    output = multiprocessing.Queue(5)

    main_process = multiprocessing.Process(target=main_process, args=(input, output))
    main_process.daemon = True
    child_process = multiprocessing.Process(target=child_process, args=(input, output))
    child_process.daemon = False

    main_process.start()
    child_process.start()

    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    while True:
        _, frame = video_capture.read()

        input.put(frame)

        cv2.imshow('Video', output.get())

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
