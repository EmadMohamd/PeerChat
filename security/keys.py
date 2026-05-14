from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os
import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
def private_key_file():
    return BASE_DIR / "keys" / f"private{config.PEER_ID}.pem"

def public_key_file():
    return BASE_DIR / "keys" / f"public{config.PEER_ID}.pem"


def generate_keys():

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    public_key = private_key.public_key()

    return private_key, public_key


def save_keys(private_key, public_key):

    with open(private_key_file(), "wb") as f:

        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    with open(public_key_file(), "wb") as f:

        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )


def load_private_key():

    with open(private_key_file(), "rb") as f:

        return serialization.load_pem_private_key(
            f.read(),
            password=None
        )


def load_public_key():

    with open(public_key_file(), "rb") as f:

        return serialization.load_pem_public_key(
            f.read()
        )


def public_key_to_pem(public_key):

    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()


def pem_to_public_key(pem_data):

    return serialization.load_pem_public_key(
        pem_data.encode()
    )


def ensure_keys_exist():

    if not os.path.exists(private_key_file()):

        private_key, public_key = generate_keys()

        save_keys(private_key, public_key)

        print("[KEYS GENERATED]")