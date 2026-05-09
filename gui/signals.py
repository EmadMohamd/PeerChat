from PyQt6.QtCore import QObject, pyqtSignal


class EventBus(QObject):

    message_received = pyqtSignal(str)

    peer_connected = pyqtSignal(str)


event_bus = EventBus()