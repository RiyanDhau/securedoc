import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QMessageBox, QFormLayout
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
        self.setWindowTitle("Secure Document Management System - Login")
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(420, 320)
        self._build_ui()

    def _build_ui(self):
        outer_layout = QVBoxLayout()

        title = QLabel("ByteForge")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        outer_layout.addWidget(title)

        tabs = QTabWidget()
        tabs.addTab(self._build_login_tab(), "Login")
        tabs.addTab(self._build_register_tab(), "Register")
        outer_layout.addWidget(tabs)

        self.setLayout(outer_layout)

    def _build_login_tab(self) -> QWidget:
        tab = QWidget()
        layout = QFormLayout()

        self.login_username = QLineEdit()
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)

        layout.addRow("Username:", self.login_username)
        layout.addRow("Password:", self.login_password)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self._handle_login)
        layout.addRow(login_btn)

        # Allow pressing Enter to submit
        self.login_password.returnPressed.connect(self._handle_login)

        tab.setLayout(layout)
        return tab

    def _build_register_tab(self) -> QWidget:
        tab = QWidget()
        layout = QFormLayout()

        self.reg_username = QLineEdit()
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_strength_label = QLabel("")

        self.reg_password.textChanged.connect(self._update_strength_label)

        layout.addRow("Username:", self.reg_username)
        layout.addRow("Password:", self.reg_password)
        layout.addRow("Strength:", self.reg_strength_label)

        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self._handle_register)
        layout.addRow(register_btn)

        tab.setLayout(layout)
        return tab

    def _update_strength_label(self, text: str) -> None:
        if not text:
            self.reg_strength_label.setText("")
            return

        rating, missing = password_tools.check_strength(text)
        color = {"Weak": "red", "Moderate": "orange", "Strong": "green"}.get(rating, "black")
        self.reg_strength_label.setText(rating)
        self.reg_strength_label.setStyleSheet(f"color: {color}; font-weight: bold;")

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
