import sys
import threading
import time
import socket
import subprocess
from PyQt6.QtWidgets import QApplication
from pathlib import Path
import config
from network.server import start_server
from network.client import init_client_keys
from security.keys import ensure_keys_exist
from gui.app import start_gui
from gui.config_window import ConfigWindow

sys.path.insert(0, str(Path(__file__).resolve().parent))


def get_runtime_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip


def start_network(my_port):
    """Launches the localized binding instance safely."""
    server_thread = threading.Thread(target=start_server, args=(my_port,), daemon=True)
    server_thread.start()
    print(f"[MAIN] Server process bound and running on listening port: {my_port}")

    time.sleep(1)
    print(f"[MAIN] Background peer discovery system fully deployed.")


def spawn_background_bootstraps():
    """Spawns dedicated bootstrap nodes quietly behind the scenes if not already running."""
    print("[AUTOMATION] Checking and deploying background bootstrap cluster...")
    ports_and_names = [(9000, "Bootstrap_node_1"), (9001, "Bootstrap_node_2"), (9002, "Bootstrap_node_3")]

    for port, name in ports_and_names:
        # Check if the port is already taken to avoid double-launch errors
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                # Port is free, meaning this bootstrap isn't running yet. Spawn it!
                subprocess.Popen([sys.executable, __file__, str(port), name])
                print(f"[AUTOMATION] Spawned background handler: {name} on port {port}")
                time.sleep(0.2)  # Slight staggering gap
            except socket.error:
                # Port is busy, likely already running or active
                print(f"[AUTOMATION] Port {port} is occupied. Skipping auto-spawn for {name}.")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if len(sys.argv) < 3:
        # Only run background processes if we are starting a normal client window
        spawn_background_bootstraps()
        time.sleep(0.5)

        config_screen = ConfigWindow()
        config_screen.show()
        app.exec()

        if config_screen.username is None or config_screen.port is None:
            print("[MAIN] Configuration setup cancelled. Exiting.")
            sys.exit(0)

        runtime_port = config_screen.port
        runtime_user = config_screen.username
    else:
        runtime_port = int(sys.argv[1])
        runtime_user = sys.argv[2]

    config.PORT = runtime_port
    config.USERNAME = runtime_user

    node_id = ensure_keys_exist()
    config.PEER_ID = node_id

    current_lan_ip = get_runtime_lan_ip()

    print(f"--- PeerChat Network Mode ---")
    print(f"User Identification: {config.USERNAME}")
    print(f"Cryptographic ID:    {config.PEER_ID}")
    print(f"Local Network IP:    {current_lan_ip}")
    print(f"Listening Port:      {config.PORT}")
    print(f"-----------------------------")

    init_client_keys()

    network_thread = threading.Thread(target=start_network, args=(config.PORT,), daemon=True)
    network_thread.start()

    # If this is an auto-spawned bootstrap node, do not render a GUI window!
    if "Bootstrap_node" in config.USERNAME:
        print(f"[BOOTSTRAP] Dedicated routing node '{config.USERNAME}' online. Keeping socket alive.")
        # Infinite blocking loop for terminal nodes so they stay running
        while True:
            time.sleep(3600)
    else:
        # Pass primary application execution over to the main chat dashboard
        start_gui()