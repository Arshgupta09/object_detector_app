from multiprocessing.connection import Client
import multiprocessing
from pickle2reducer import Pickle2Reducer

multiprocessing.context._default_context.reducer = Pickle2Reducer()

dest = ("192.168.1.100", 5000)
conn = Client(dest)

i = 0
while i < 10:
    data = i
    conn.send(data)
    recv_data = conn.recv()
    print("valor %d --> %d" % (i, recv_data))
    i += 1
