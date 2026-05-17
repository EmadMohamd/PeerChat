import threading

network_lock = threading.Lock()
authenticated_peers = set()
peer_public_keys = {}
pending_challenges = {}
known_peers = set()
connected_peers = {}       # {(ip, port): socket}
peer_ids = {}

BOOTSTRAP_PEERS = [("127.0.0.1", 9000), ("127.0.0.1", 9001), ("127.0.0.1", 9002)]

def add_known_peer(ip, port):
    import config
    if ip == "127.0.0.1" and int(port) == int(config.PORT): return
    with network_lock: known_peers.add((ip, int(port)))

def register_authenticated_connection(ip, port, sock, peer_id):
    with network_lock:
        if (ip, port) in connected_peers:
            old_sock = connected_peers[(ip, port)]
            if old_sock != sock:
                try:
                    authenticated_peers.discard(old_sock)
                    for d in [peer_ids, peer_public_keys, pending_challenges]: d.pop(old_sock, None)
                    old_sock.close()
                except: pass
        connected_peers[(ip, port)] = sock
        authenticated_peers.add(sock)
        peer_ids[sock] = peer_id
    add_known_peer(ip, port)

def remove_connection(sock):
    with network_lock:
        try:
            authenticated_peers.discard(sock)
            for d in [peer_ids, peer_public_keys, pending_challenges]: d.pop(sock, None)
            for addr, s in list(connected_peers.items()):
                if s == sock: del connected_peers[addr]
            sock.close()
        except: pass

def get_all_connections():
    with network_lock: return list(connected_peers.values())

def get_authenticated_peer_addresses():
    with network_lock: return list(connected_peers.keys())