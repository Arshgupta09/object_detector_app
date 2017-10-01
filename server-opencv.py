import argparse
import socket
import pickle as pickle

BUFF_SIZE = 6553600

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--host', type=str, default='localhost', help='name or IP of the host that process the images')
    parser.add_argument('--port', type=int, default=5000, help='image processor server TCP port')
    args = parser.parse_args()
    orig = ('', args.port)  # bind all addresses

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(orig)
    tcp.listen(1)
    print('binding completado')
    while True:
        con, cliente = tcp.accept()
        msg = con.recv(BUFF_SIZE)
        obj = pickle.loads(msg)
        print('mensagem recebida de ', cliente)
        con.send(msg)
        con.close()
    tcp.close()
