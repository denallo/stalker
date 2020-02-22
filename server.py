# coding: utf-8
import zmq
import time
import threading


def serve(socket):
    msg = socket.recv()
    print(msg.decode())
    time.sleep(3)
    socket.send(msg)
    socket.close()


def listen():
    context = zmq.Context()
    listener = context.socket(zmq.REP)
    listener.bind("tcp://*:20000")
    while True:
        listener.recv()
        worker = context.socket(zmq.REP)
        try:
          # try to open a random port for the client
          port = worker.bind_to_random_port('tcp://*')
          thread = threading.Thread(target=serve, args=[worker])
          thread.start()
        except zmq.ZMQBindError:
          port = -1
        listener.send(str(port).encode())


if __name__ == '__main__':
  try:
    listen()
  except Exception as e:
    print(repr(e))
