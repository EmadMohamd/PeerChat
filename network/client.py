import socket
import threading
import config
from network.protocol import create_packet
from network.discover import connected_peers, known_peers
from security.keys import load_private_key, load_public_key, public_key_to_pem
from security.crypto import sign_message

private_key = None
public_key = None

def init_client_keys():
    global private_key, public_key
    from security.keys import ensure_keys_exist
    ensure_keys_exist()
    private_key = load_private_key()
    public_key = load_public_key()

def connect_to_peer(ip, port, receive_loop):
    if (ip, port) in connected_peers:
        return

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        connected_peers[(ip, port)] = sock
        known_peers.add((ip, port))

        thread = threading.Thread(target=receive_loop, args=(sock,))
        thread.daemon = True
        thread.start()

        # Start mutual handshake
        send_identity(sock)
        sock.send(create_packet("peer_request", {}))

    except Exception as e:
        print(f"[FAILED] {ip}:{port} -> {e}")

def send_identity(sock):
    packet = create_packet("identity", {
        "peer_id": config.PEER_ID,
        "public_key": public_key_to_pem(public_key)
    })
    sock.send(packet)

def handle_challenge(sock, challenge):
    signature = sign_message(private_key, challenge)
    packet = create_packet("challenge_response", {
        "signature": signature.hex()
    })
    sock.send(packet)


def send_chat_message(message, target_peer_id=None):
    packet = create_packet("chat", {
        "sender": config.PEER_ID,
        "recipient": target_peer_id,  # None for global/broadcast
        "message": message
    })

    for sock in list(connected_peers.values()):
        try:
            sock.send(packet)
        except:
            pass