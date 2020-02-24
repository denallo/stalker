# coding: utf-8
import zmq
import json
import time

HOST = 'localhost'
PORT = 38741
LISTENING_PORT = 3874
SHADOW_CHANNEL = False


def get(url):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://%s:%d" % (HOST, PORT))
    req = {'shadow':SHADOW_CHANNEL, 'url':url}
    pkg = json.dumps(req)
    socket.send(pkg.encode())
    start = time.time()
    rsp = socket.recv()
    end = time.time()
    print('cost: %ss rsp:%s' % (end-start, rsp.decode()))
    socket.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--listening-port', help="local listening port", default=3874)
    parser.add_argument('-s', '--server-address', help='host address of proxy service', default='127.0.0.1')
    parser.add_argument('-p', '--port', help='listening port of proxy service', default=38741)
    parser.add_argument('--logging-dir', action='store_true')
    parser.add_argument('-c', '--configure-file', action='store_true')
    parser.add_argument('-u', help='http/https url for request with [get] method', default='')
    parser.add_argument('--shadow-channel', help="", action='store_true', default=False)
    args = parser.parse_args()
    HOST = args.server_address
    PORT = args.port
    LISTENING_PORT = args.listening_port
    SHADOW_CHANNEL = args.shadow_channel

    if args.u != '':
        print(get(args.u))

