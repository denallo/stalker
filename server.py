# coding: utf-8
import zmq
import time
import threading

PORT_FRONTEND = 38741
PORT_BACKEND = 5556
WORKER_CNT = 10


def work():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.connect("tcp://localhost:%s" % PORT_BACKEND)
    while True:
        message = socket.recv()
        print(message.decode())
        time.sleep(1)
        socket.send(message)


def dispath():
    try:
        context = zmq.Context(1)
        frontend = context.socket(zmq.XREP)
        frontend.bind("tcp://*:%d" % PORT_FRONTEND)
        backend = context.socket(zmq.XREQ)
        backend.bind("tcp://127.0.0.1:%d" % PORT_BACKEND)
        zmq.device(zmq.QUEUE, frontend, backend)
    except Exception as e:
        print(e)
    finally:
        frontend.close()
        backend.close()
        context.term()


if __name__ == "__main__":
    dispathcer = threading.Thread(target=dispath)
    dispathcer.start()

    workers = []
    for i in range(WORKER_CNT):
        worker = threading.Thread(target=work)
        worker.start()
        workers.append(worker)
    for worker in workers:
        worker.join()

    dispathcer.join()
