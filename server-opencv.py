import socket
import cPickle as cp

HOST = ''              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
orig = (HOST, PORT)

if __name__ == '__main__':
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(orig)
    print 'binding completado'
    while True:
        msg, cliente = udp.recvfrom(1024)
        obj = cp.loads(msg)

        print 'mensagem recebida de ', cliente, ':', obj
    udp.close()
