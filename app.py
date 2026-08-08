import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer

from login_window import LoginWindow
from main_window import MainWindow
from crypto_utils import generate_key


class SplashScreen(QLabel):
    """Simple splash screen that shows a resized image."""

    def __init__(self):
        super().__init__()

        img_path = os.path.join(os.path.dirname(__file__), "assets", "bgimg.png")
        pixmap = QPixmap(img_path)

        #  Resize image (scale down)
        scaled_pixmap = pixmap.scaled(
            500, 300,  #  adjust this (width, height)
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.setPixmap(scaled_pixmap)

        # Remove window frame
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Resize window to new image size
        self.resize(scaled_pixmap.size())

        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )


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
    # Ensure encryption key exists
    if not os.path.exists("data/secret.key"):
        os.makedirs("data", exist_ok=True)
        generate_key()

    app = QApplication(sys.argv)

    # App icon
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Stylesheet
    style_path = os.path.join(os.path.dirname(__file__), "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())

    # 🔥 Show Splash Screen
    splash = SplashScreen()
    splash.show()

    # Start main app after 2 seconds
    def start_app():
        splash.close()
        controller = App()
        app.controller = controller  # prevent garbage collection

    QTimer.singleShot(2000, start_app)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()