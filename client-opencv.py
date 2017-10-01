import socket
import cPickle as cp

HOST = 'localhost'  # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

if __name__ == '__main__':
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (HOST, PORT)

    obj = {1: 2, 3: 4, 5: 6}
    print 'preparando para enviar:', obj
    msg = cp.dumps(obj, cp.HIGHEST_PROTOCOL)
    print 'enviando para', dest
    udp.sendto(msg, dest)
    print 'msg enviada'
    udp.close()
