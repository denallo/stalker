# coding: utf-8
import zmq

HOST = 'localhost'
PORT = 38741
LISTENING_PORT = 3874


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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--listening-port', help="local listening port", default=3874)
    parser.add_argument('-s', '--server-address', help='host address of proxy service', default='127.0.0.1')
    parser.add_argument('-p', '--port', help='listening port of proxy service', default=38741)
    parser.add_argument('--logging-dir', action='store_true')
    parser.add_argument('-c', '--configure-file', action='store_true')
    args = parser.parse_args()
    HOST = args.server_address
    PORT = args.port
    LISTENING_PORT = args.listening_port

    threads = []
    import threading
    for i in range(0, 100):
        thread = threading.Thread(target=get, args=[])
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
