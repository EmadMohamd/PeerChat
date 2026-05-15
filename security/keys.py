import hashlib
import config
import os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

BASE_DIR = Path(__file__).resolve().parent.parent
KEYS_DIR = BASE_DIR / "keys"


# --- HELPER LOGIC ---

def get_paths():
    """Centrally manages naming based on config.USERNAME."""
    name = config.USERNAME
    return {
        "priv": KEYS_DIR / f"{name}_private.pem",
        "pub": KEYS_DIR / f"{name}_public.pem"
    }


# --- RESTORED ORIGINAL FUNCTIONS ---

def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key


def save_keys(private_key, public_key):
    KEYS_DIR.mkdir(exist_ok=True)
    paths = get_paths()

    with open(paths["priv"], "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(paths["pub"], "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))


def load_private_key():
    paths = get_paths()
    with open(paths["priv"], "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None
        )


def load_public_key():
    paths = get_paths()
    with open(paths["pub"], "rb") as f:
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
    """Generates keys if missing and updates config.PEER_ID."""
    paths = get_paths()

    if not paths["priv"].exists():
        private_key, public_key = generate_keys()
        save_keys(private_key, public_key)
        print(f"[KEYS GENERATED] New identity created for: {config.USERNAME}")

    # Derive ID and update global config
    with open(paths["pub"], "rb") as f:
        pub_bytes = f.read()
        hash_str = hashlib.sha256(pub_bytes).hexdigest()
        config.PEER_ID = f"{config.USERNAME}:{hash_str[:10]}"

    return config.PEER_ID