import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QMessageBox, QFormLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

import auth
import password_tools


class LoginWindow(QWidget):
    """Login / Register window. On success, calls on_login_success(username)."""

    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("STEGANSHIELD - Login")

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setFixedSize(760, 460)
        self._build_ui()

    def _build_ui(self):
        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        outer_layout.addWidget(self._build_brand_panel(), 2)
        outer_layout.addWidget(self._build_form_panel(), 3)

        self.setLayout(outer_layout)

    # ---------------- Left brand panel ----------------

    def _build_brand_panel(self) -> QWidget:
        from PyQt5.QtWidgets import QLabel, QVBoxLayout
        from PyQt5.QtGui import QPixmap
        from PyQt5.QtCore import Qt

        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "brandimg.png"
        )

        label = QLabel()

        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)

            # 🔥 SCALE IMAGE TO FILL PANEL
            label.setPixmap(pixmap)
            label.setScaledContents(True)   # 👈 THIS is key
        else:
            label.setText("Image not found")
            label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        panel.setLayout(layout)

        return panel

    # ---------------- Right form panel ----------------

    def _build_form_panel(self) -> QWidget:
        panel = QWidget()

        layout = QVBoxLayout()
        layout.setContentsMargins(48, 48, 48, 40)
        layout.setSpacing(6)

        heading = QLabel("Welcome")
        heading.setProperty("role", "title")

        subheading = QLabel("Sign in to your account or create a new one")
        subheading.setProperty("role", "subtitle")

        layout.addWidget(heading)
        layout.addWidget(subheading)
        layout.addSpacing(18)

        tabs = QTabWidget()
        tabs.addTab(self._build_login_tab(), "Login")
        tabs.addTab(self._build_register_tab(), "Register")
        layout.addWidget(tabs)
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _build_login_tab(self) -> QWidget:
        tab = QWidget()
        layout = QFormLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(2, 20, 2, 8)
        layout.setLabelAlignment(Qt.AlignLeft)

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Enter your username")
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter your password")
        self.login_password.setEchoMode(QLineEdit.Password)

        layout.addRow("Username", self.login_username)
        layout.addRow("Password", self.login_password)

        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(38)
        login_btn.clicked.connect(self._handle_login)
        layout.addRow(login_btn)

        self.login_password.returnPressed.connect(self._handle_login)

        tab.setLayout(layout)
        return tab

    def _build_register_tab(self) -> QWidget:
        tab = QWidget()
        layout = QFormLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(2, 20, 2, 8)
        layout.setLabelAlignment(Qt.AlignLeft)

        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Choose a username")
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Choose a password")
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_strength_label = QLabel("")

        self.reg_password.textChanged.connect(self._update_strength_label)

        layout.addRow("Username", self.reg_username)
        layout.addRow("Password", self.reg_password)
        layout.addRow("Strength", self.reg_strength_label)

        register_btn = QPushButton("Create account")
        register_btn.setMinimumHeight(38)
        register_btn.clicked.connect(self._handle_register)
        layout.addRow(register_btn)

        tab.setLayout(layout)
        return tab

    def _update_strength_label(self, text: str) -> None:
        if not text:
            self.reg_strength_label.setText("")
            return

        rating, missing = password_tools.check_strength(text)
        color = {"Weak": "#DC2626", "Moderate": "#D97706", "Strong": "#16A34A"}.get(rating, "#1E293B")
        self.reg_strength_label.setText(rating)
        self.reg_strength_label.setStyleSheet(f"color: {color}; font-weight: 700;")

    def _handle_login(self) -> None:
        username = self.login_username.text().strip()
        password = self.login_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Missing Fields", "Please enter both username and password.")
            return

        if auth.login_user(username, password):
            self.on_login_success(username)
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")

    def _handle_register(self) -> None:
        username = self.reg_username.text().strip()
        password = self.reg_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Missing Fields", "Please enter both username and password.")
            return

        if auth.register_user(username, password):
            QMessageBox.information(self, "Success", f"User '{username}' registered. You can now login.")
            self.reg_username.clear()
            self.reg_password.clear()
        else:
            QMessageBox.critical(self, "Registration Failed", "Username already exists.")