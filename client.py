# coding: utf-8
import zmq
import json

HOST = ''
PORT = ''


def __connect():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://%s:%s" % (HOST, PORT))
    socket.send(''.encode())
    port = socket.recv().decode()
    socket.disconnect("tcp://%s:%s" % (HOST, PORT))
    socket.connect("tcp://%s:%s" % (HOST, port))
    return socket


def __check_ret_code(code):
    pass


def set_proxy(host='127.0.0.1', port='20000'):
    global HOST, PORT
    HOST = host
    PORT = port
    socket = __connect()
    socket.send("hello".encode())
    rsp = socket.recv()
    if rsp:
        return True
    return False


def get(url=''):
    socket = __connect()

    # package = {'METHOD': 'get', 'URL': url}
    # socket.send(json.dumps(package))

    # rsp = json.loads(socket.recv())
    # code, data = rsp['CODE'], rsp['CONTENT']
    # __check_ret_code(code)
    # return data
    thread_id = str('[%04X] ' % threading.currentThread().ident)
    socket.send(thread_id.encode())
    rsp = socket.recv()
    if thread_id == rsp.decode():
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
