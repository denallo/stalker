# coding: utf-8
import zmq
import json
import time
import secp256k1 as ecc

HOST = 'localhost'
PORT = 38741
LISTENING_PORT = 3874
SHADOW_CHANNEL = False
SOCKET = None
PRIVATE_KEY = -1
PUBLIC_KEY = (-1, -1)
PEER_PUBKEY = (-1, -1)


def get(url):
    global SOCKET
    req = {'shadow':SHADOW_CHANNEL, 'url':url}
    context = json.dumps(req)
    tp1 = time.time()
    deckey_1, deckey_2, enc_context = ecc.encrypt(context, PRIVATE_KEY, PEER_PUBKEY)
    enc_pkg = bytes.fromhex("%s%s%s" % (
        ecc.serialize_key_pair(deckey_1),
        ecc.serialize_key_pair(deckey_2),
        enc_context))
    tp2 = time.time()
    SOCKET.send(enc_pkg)
    rsp = SOCKET.recv()
    rsp = ''.join(['%02X' % x for x in rsp])
    tp3 = time.time()
    decrypt_keys_text, enc_rsp = rsp[:256], rsp[256:]
    deckey_1 = ecc.deserialize_key_pair(decrypt_keys_text[:128])
    deckey_2 = ecc.deserialize_key_pair(decrypt_keys_text[128:])
    decrypt_keys = (deckey_1, deckey_2)
    dec_rsp = ecc.decrypt(enc_rsp, PRIVATE_KEY, decrypt_keys)
    tp4 = time.time()
    print('cost: package=%.2f, network=%.2f, unpack=%.2f' % (tp2-tp1, tp3-tp2, tp4-tp3))
    print(dec_rsp)


def connect():
    global SOCKET, PRIVATE_KEY, PUBLIC_KEY
    context = zmq.Context()
    SOCKET = context.socket(zmq.REQ)
    SOCKET.connect("tcp://%s:%d" % (HOST, PORT))
    PRIVATE_KEY = ecc.gen_private_key()
    PUBLIC_KEY = ecc.gen_public_key(PRIVATE_KEY)
    # 发送公钥给服务端
    SOCKET.send(bytes.fromhex('FF01%s' % ecc.serialize_key_pair(PUBLIC_KEY)))
    # 接收服务端公钥
    rsp = SOCKET.recv()
    if (rsp[0], rsp[1]) != (0xFF, 0x01):
        raise Exception('unknown frame: %02X %02X' % (rsp[0], rsp[1]))
    key_text = ''.join(['%02X' % x for x in rsp[2:]])
    global PEER_PUBKEY
    PEER_PUBKEY = ecc.deserialize_key_pair(key_text)


def disconnect():
    global SOCKET, PRIVATE_KEY, PUBLIC_KEY, PEER_PUBKEY
    SOCKET.close()
    SOCKET = None
    PRIVATE_KEY = -1
    PUBLIC_KEY = (-1, -1)
    PEER_PUBKEY = (-1, -1)


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

    connect()
    if args.u != '':
        print(get(args.u))
    disconnect()

