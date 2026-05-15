# network/discover.py

authenticated_peers = set()
peer_public_keys = {}
pending_challenges = {}
known_peers = set()
connected_peers = {}
peer_ids = {} # {socket_object: "Peer_Name"}

BOOTSTRAP_PEERS = [
    ("127.0.0.1", 9000),
    ("127.0.0.1", 9001),
    ("127.0.0.1", 9002),
]

def add_known_peer(ip, port):
    known_peers.add((ip, port))

def remove_connection(ip, port):
    """
    Enhanced cleanup: Removes the socket from connection tracking
    AND authentication tracking.
    """
    if (ip, port) in connected_peers:
        sock = connected_peers[(ip, port)]
        try:
            # Clean up all tracking related to this specific socket object
            authenticated_peers.discard(sock)
            if sock in peer_public_keys: del peer_public_keys[sock]
            if sock in pending_challenges: del pending_challenges[sock]
            sock.close()
        except:
            pass
        del connected_peers[(ip, port)]

def is_connected(ip, port):
    return (ip, port) in connected_peers

def get_all_connections():
    return list(connected_peers.values())