import sys

from PyQt6.QtWidgets import QApplication

from gui.chat_window import ChatWindow


def start_gui():

    app = QApplication(sys.argv)

    window = ChatWindow()

    window.show()

    sys.exit(app.exec())