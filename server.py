# coding: utf-8
import zmq
import threading
import socket
import socks
import requests
import json
import time
import secp256k1 as ecc


PORT_FRONTEND = 38741
PORT_BACKEND = 5556
WORKER_CNT = 10
AGENT_HOST = '127.0.0.1'
AGENT_PORT = 3874
SHADOW_CHANNEL = False
PRIVATE_KEY = -1
PUBLIC_KEY = (-1, -1)
PEER_PUBKEY = (-1, -1)


def work():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.REP)
    zmq_socket.connect("tcp://localhost:%s" % PORT_BACKEND)
    no_proxy_socket = socket.socket

    if SHADOW_CHANNEL:
        socks.set_default_proxy(socks.SOCKS5, AGENT_HOST, AGENT_PORT)

    global PEER_PUBKEY
    while True:
        msg_bytes = zmq_socket.recv()
        msg = ''.join(['%02X' % x for x in msg_bytes])
        if (msg_bytes[0], msg_bytes[1]) == (0xFF, 0x01):
            # 解析客户端公钥
            PEER_PUBKEY = ecc.deserialize_key_pair(msg[4:])
            # 发送服务端公钥
            zmq_socket.send(bytes.fromhex('FF01%s' % ecc.serialize_key_pair(PUBLIC_KEY)))
        else:
            # 解密数据包
            decrypt_keys_text, enc_rsp = msg[:256], msg[256:]
            deckey_1 = ecc.deserialize_key_pair(decrypt_keys_text[:128])
            deckey_2 = ecc.deserialize_key_pair(decrypt_keys_text[128:])
            decrypt_keys = (deckey_1, deckey_2)
            # decrypt_keys = ecc.deserialize_key_pair(decrypt_keys_text)
            json_str = ecc.decrypt(enc_rsp, PRIVATE_KEY, decrypt_keys).strip(b'\x00'.decode())
            dec_msg = json.loads(json_str)
            shadow = dec_msg['shadow']
            url = dec_msg['url']
            if shadow and SHADOW_CHANNEL:
                socket.socket = socks.socksocket
            else:
                socket.socket = no_proxy_socket
            rsp = requests.get(url).content.decode()
            # 加密响应数据
            deckey_1, deckey_2,  enc_context = ecc.encrypt(rsp, PRIVATE_KEY, PEER_PUBKEY)
            # decrypt_keys = (deckey_x, deckey_y)
            # enc_pkg = bytes.fromhex("%s%s" % (ecc.serialize_key_pair(decrypt_keys), enc_context))
            enc_pkg = bytes.fromhex("%s%s%s" % (
                ecc.serialize_key_pair(deckey_1),
                ecc.serialize_key_pair(deckey_2),
                enc_context))
            zmq_socket.send(enc_pkg)


def dispatch():
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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--backend-port', help="", default=5556, type=int)
    parser.add_argument('-f', '--frontend-port', help="", default=38741, type=int)
    parser.add_argument('-w', '--worker-count', help="", default=100, type=int)
    parser.add_argument('--agent-port', help="", default=3874, type=int)
    parser.add_argument('--agent-host', help="", default='127.0.0.1')
    parser.add_argument('--shadow-channel', help="", action='store_true', default=False)
    args = parser.parse_args()
    PORT_BACKEND = args.backend_port
    PORT_FRONTEND = args.frontend_port
    WORKER_CNT = args.worker_count
    AGENT_HOST = args.agent_host
    AGENT_PORT = args.agent_port
    SHADOW_CHANNEL = args.shadow_channel
    PRIVATE_KEY = ecc.gen_private_key()
    PUBLIC_KEY = ecc.gen_public_key(PRIVATE_KEY)


    dispatcher = threading.Thread(target=dispatch)
    dispatcher.start()

    workers = []
    for i in range(WORKER_CNT):
        worker = threading.Thread(target=work)
        worker.start()
        workers.append(worker)
    for worker in workers:
        worker.join()

    dispatcher.join()
