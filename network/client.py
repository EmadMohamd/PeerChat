import socket
import threading

from network.protocol import create_packet

from network.discover import (
    connected_peers,
    known_peers
)

from security.keys import (
    load_private_key,
    load_public_key,
    public_key_to_pem
)

from security.crypto import sign_message


private_key = None
public_key = None

def init_client_keys():
    global private_key
    global public_key
    private_key = load_private_key()
    public_key = load_public_key()



def connect_to_peer(ip, port, receive_loop):

    if (ip, port) in connected_peers:
        return

    try:

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.connect((ip, port))

        connected_peers[(ip, port)] = sock

        known_peers.add((ip, port))

        print(f"[CONNECTED TO] {ip}:{port}")

        thread = threading.Thread(
            target=receive_loop,
            args=(sock,)
        )

        thread.daemon = True
        thread.start()

        send_identity(sock)

        request_peer_list(sock)

    except Exception as e:

        print(f"[FAILED] {ip}:{port} -> {e}")


def send_identity(sock):

    packet = create_packet(
        "identity",
        {
            "peer_id": "peer",
            "public_key": public_key_to_pem(public_key)
        }
    )

    sock.send(packet)


def request_peer_list(sock):

    packet = create_packet(
        "peer_request",
        {}
    )

    sock.send(packet)


def send_chat_message(message):

    packet = create_packet(
        "chat",
        {
            "sender": "peer",
            "message": message
        }
    )

    for sock in connected_peers.values():

        try:
            sock.send(packet)

        except:
            pass


def handle_challenge(sock, challenge):

    signature = sign_message(
        private_key,
        challenge
    )

    packet = create_packet(
        "challenge_response",
        {
            "signature": signature.hex()
        }
    )

    sock.send(packet)