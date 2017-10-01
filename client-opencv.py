import socket
import cPickle as cp
import cv2

HOST = 'localhost'  # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

if __name__ == '__main__':
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (HOST, PORT)

    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    while True:
        _, frame = video_capture.read()
        # convert frame to sent via sockets to server
        msg = cp.dumps(frame, cp.HIGHEST_PROTOCOL)
        print 'enviando para', dest
        # send message
        udp.sendto(msg, dest)
        print 'msg enviada'
        # receive message (frame tagged) from server
        msg, cliente = udp.recvfrom(1024)
        print 'mensagem recebida'
        new_frame = cp.loads(msg)
        # display image
        cv2.imshow('Video', new_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    udp.close()
