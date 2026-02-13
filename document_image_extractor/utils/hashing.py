import hashlib

def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()
