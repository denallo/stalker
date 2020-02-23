# coding: utf-8
import zmq
import json

HOST = ''
PORT = -1


def set_proxy(host='localhost', port=38741):
    global HOST, PORT
    HOST = host
    PORT = port


def get(url=''):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://%s:%d" % (HOST, PORT))
    ident = threading.currentThread().ident
    msg = str('[%04X] ' % ident)
    socket.send(msg.encode())
    frame = socket.recv()
    if msg == frame.decode():
        print('o')
    else:
        print('x')
    socket.close()


if __name__ == '__main__':
    set_proxy()
    import threading
    threads = []
    for i in range(0, 100):
        thread = threading.Thread(target=get, args=[])
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
