from PyQt6.QtCore import QObject, pyqtSignal

from PyQt6.QtCore import QObject, pyqtSignal

class EventBus(QObject):

    message_received = pyqtSignal(str, str, str)

# Global instance
event_bus = EventBus()