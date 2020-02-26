# coding: utf-8
import tools
import secrets
from ec import EC, Coord


'''secp256k1椭圆曲线参数'''
a, b = 0, 7
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
ec_secp256k1 = EC(a, b, p)


@tools.time_this_function
def gen_public_key(prikey):
    pubkey = ec_secp256k1.mul(Coord(G), prikey)
    return pubkey.x, pubkey.y


def gen_private_key():
    return secrets.randbelow(n)


def __gen_encrypt_key():
    random = secrets.randbelow(n)
    enckey = ec_secp256k1.mul(Coord(G), random)
    return enckey


@tools.time_this_function
def __gen_decrypt_key(prikey, peer_pubkey, enckey):
    c1 = ec_secp256k1.add(enckey, ec_secp256k1.mul(Coord(peer_pubkey), prikey))
    c2 = ec_secp256k1.mul(Coord(G), prikey)
    return c1, c2


@tools.time_this_function
def encrypt(plain_text, prikey, peer_pubkey):
    m = __gen_encrypt_key()
    c1, c2 = __gen_decrypt_key(prikey, peer_pubkey, m)
    num = int.from_bytes(plain_text.encode('utf-8'), 'big')
    enc_text = hex(m.x * num)[2:]
    return (c1.x, c1.y), (c2.x, c2.y), enc_text


@tools.time_this_function
def decrypt(enc_text, prikey, deckeys):
    c1, c2 = Coord(deckeys[0]), Coord(deckeys[1])
    kC2 = ec_secp256k1.mul(c2, prikey)
    neg_kC2 = ec_secp256k1.neg(kC2)
    enckey = ec_secp256k1.add(c1, neg_kC2)
    num = int(enc_text, 16)//enckey.x
    bits = num.to_bytes(len(enc_text)//2, 'big')
    plain_text = bits.decode('utf-8')
    return plain_text


def serialize_key_pair(pair):
    text_x = hex(pair[0])[2:]
    text_y = hex(pair[1])[2:]
    while len(text_x) < 64:
        text_x = '0' + text_x
    while len(text_y) < 64:
        text_y = '0' + text_y
    assert len(text_x) == 64
    assert len(text_y) == 64
    return text_x + text_y


def deserialize_key_pair(text):
    assert len(text) == 128
    x, y = int(text[:64], 16), int(text[64:], 16)
    return x, y


if __name__ == '__main__':
    # user-a 生成密钥对
    private_a = gen_private_key()
    public_a = gen_public_key(private_a)
    # user-b 生成密钥对
    private_b = gen_private_key()
    # user-b 加密明文
    text = 'The Times 03/Jan/2009 Chancellor on brink of second bailout for banks.'
    deckey1, deckey2, secrets_text = encrypt(text, private_b, public_a)
    # user-a 解密文
    print(decrypt(secrets_text, private_a, (deckey1, deckey2)))
