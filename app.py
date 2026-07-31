import sys
import os
from PyQt5.QtWidgets import QApplication

from login_window import LoginWindow
from main_window import MainWindow
from crypto_utils import generate_key


class App:
    """Manages switching between the login window and the main window."""

    def __init__(self):
        self.login_window = None
        self.main_window = None
        self.show_login()

    def show_login(self):
        self.login_window = LoginWindow(on_login_success=self.show_main)
        self.login_window.show()

    def show_main(self, username: str):
        self.login_window.close()
        self.main_window = MainWindow(username, on_logout=self.show_login)
        self.main_window.show()


def main():
    # Ensure encryption key exists before anything else runs
    if not os.path.exists("data/secret.key"):
        os.makedirs("data", exist_ok=True)
        generate_key()

    app = QApplication(sys.argv)
    controller = App()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
