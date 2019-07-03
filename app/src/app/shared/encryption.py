import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


def encrypt(raw, password):
    if isinstance(password, str):
        password = password.encode('utf-8')
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8')
    private_key = hashlib.sha256(password).digest()
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw))


def decrypt(enc, password):
    if isinstance(password, str):
        password = password.encode('utf-8')
    if isinstance(enc, str):
        enc = enc.encode('utf-8')
    private_key = hashlib.sha256(password).digest()
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))
