import sys
import threading
import time

from network.server import (
    start_server,
    receive_loop
)

from network.client import (
    connect_to_peer,
    init_client_keys
)
from network.discover import (
    BOOTSTRAP_PEERS
)

from security.keys import (
    ensure_keys_exist

)

from gui.app import start_gui


def start_network(port):

    server_thread = threading.Thread(
        target=start_server,
        args=(port,)
    )

    server_thread.daemon = True

    server_thread.start()

    time.sleep(2)

    for ip, port in BOOTSTRAP_PEERS:

        if port != MY_PORT:

            connect_to_peer(
                ip,
                port,
                receive_loop
            )


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print("Usage:")
        print("python main.py <port>")

        sys.exit()

    MY_PORT = int(sys.argv[1])

    ensure_keys_exist()
    init_client_keys()

    network_thread = threading.Thread(
        target=start_network,
        args=(MY_PORT,)
    )

    network_thread.daemon = True

    network_thread.start()

    start_gui()