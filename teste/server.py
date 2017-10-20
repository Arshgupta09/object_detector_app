from multiprocessing.connection import Listener

address = ("0.0.0.0", 5000)  # default bind all addresses
listener = Listener(address)  # , authkey='secret password')

while True:
    conn = listener.accept()
    client_address = listener.last_accepted  # client address
    print('station %s connected' % client_address[0])
    data = conn.recv()
    print ("recebeu %d" % data)
    data += 10
    conn.send(data)
