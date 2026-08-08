from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QMessageBox, QFormLayout, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QComboBox,
    QSpinBox, QGroupBox
)
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os

import auth
import documents
import password_tools
from stego import encode_image, decode_image


class MainWindow(QMainWindow):
    """Main application window shown after successful login."""

    def __init__(self, username: str, on_logout):
        super().__init__()
        self.username = username
        self.on_logout = on_logout

        self.setWindowTitle(f"STEGANSHIELD - {username}")
        self.setMinimumSize(800, 550)

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # Top bar with user info + logout
        top_bar_widget = QWidget()
        top_bar_widget.setObjectName("topBar")
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(16, 10, 16, 10)

        app_name_label = QLabel("STEGANSHIELD")
        app_name_label.setObjectName("appNameLabel")

        user_label = QLabel("User: " f'{self.username}')
        user_label.setObjectName("userLabel")

        logout_btn = QPushButton("Logout")
        logout_btn.setProperty("role", "secondary")
        logout_btn.setFixedWidth(90)
        logout_btn.clicked.connect(self._handle_logout)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: red;
            }
            """)

        top_bar.addWidget(app_name_label)
        top_bar.addStretch()
        top_bar.addWidget(user_label)
        top_bar.addSpacing(12)
        top_bar.addWidget(logout_btn)
        top_bar_widget.setLayout(top_bar)
        main_layout.addWidget(top_bar_widget)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._build_documents_tab(), "Documents")
        tabs.addTab(self._build_stego_tab(), "Steganography")
        tabs.addTab(self._build_password_tab(), "Password Tools")
        tabs.addTab(self._build_report_tab(), "Report")
        main_layout.addWidget(tabs)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

    # ---------------- Documents Tab ----------------

    def _build_documents_tab(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(20) 

        # Left: form for add/update
        form_box = QGroupBox("Add / Update Document")
        form_layout = QFormLayout()

        self.doc_id_input = QLineEdit()
        self.doc_id_input.setPlaceholderText("Leave blank to add new")
        self.doc_title_input = QLineEdit()
        self.doc_content_input = QTextEdit()
        self.doc_content_input.setFixedHeight(100)

        form_layout.addRow("Doc ID (for update):", self.doc_id_input)
        form_layout.addRow("Title:", self.doc_title_input)
        form_layout.addRow("Content:", self.doc_content_input)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_document)
        update_btn = QPushButton("Update")
        update_btn.clicked.connect(self._update_document)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_document)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(update_btn)
        btn_row.addWidget(delete_btn)
        form_layout.addRow(btn_row)

        search_row = QHBoxLayout()
        self.doc_search_input = QLineEdit()
        self.doc_search_input.setPlaceholderText("Search by title...")
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self._search_documents)
        refresh_btn = QPushButton("Show All")
        refresh_btn.clicked.connect(self._refresh_documents)
        search_row.addWidget(self.doc_search_input)
        search_row.addWidget(search_btn)
        search_row.addWidget(refresh_btn)
        form_layout.addRow(search_row)

        form_box.setLayout(form_layout)

        # Right: table of documents
        table_box = QGroupBox("Documents")
        table_layout = QVBoxLayout()

        self.doc_table = QTableWidget(0, 4)
        self.doc_table.setHorizontalHeaderLabels(["ID", "Title", "Owner", "Created"])
        self.doc_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.doc_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.doc_table.cellClicked.connect(self._load_selected_document)

        table_layout.addWidget(self.doc_table)
        table_box.setLayout(table_layout)

        layout.addWidget(form_box, 1)
        layout.addWidget(table_box, 2)
        tab.setLayout(layout)

        self._refresh_documents()
        return tab

    def _refresh_documents(self) -> None:
        docs = documents.list_documents()
        self._populate_doc_table(docs)

    def _search_documents(self) -> None:
        keyword = self.doc_search_input.text().strip()
        if not keyword:
            self._refresh_documents()
            return
        results = documents.search_documents(keyword)
        simplified = {
            doc_id: {"title": d["title"], "owner": d["owner"], "date_created": d["date_created"]}
            for doc_id, d in results.items()
        }
        self._populate_doc_table(simplified)

    def _populate_doc_table(self, docs: dict) -> None:
        self.doc_table.setRowCount(0)
        for row, (doc_id, doc) in enumerate(docs.items()):
            self.doc_table.insertRow(row)
            self.doc_table.setItem(row, 0, QTableWidgetItem(doc_id))
            self.doc_table.setItem(row, 1, QTableWidgetItem(doc["title"]))
            self.doc_table.setItem(row, 2, QTableWidgetItem(doc["owner"]))
            self.doc_table.setItem(row, 3, QTableWidgetItem(doc["date_created"]))

    def _load_selected_document(self, row: int, column: int) -> None:
        doc_id = self.doc_table.item(row, 0).text()
        doc = documents.view_document(doc_id)
        if doc:
            self.doc_id_input.setText(doc_id)
            self.doc_title_input.setText(doc["title"])
            self.doc_content_input.setPlainText(doc["content"])

    def _add_document(self) -> None:
        title = self.doc_title_input.text().strip()
        content = self.doc_content_input.toPlainText().strip()

        if not title or not content:
            QMessageBox.warning(self, "Missing Fields", "Title and content are required.")
            return

        try:
            doc_id = documents.add_document(title, content, self.username)
            QMessageBox.information(self, "Success", f"Document added with ID {doc_id}.")
            self._clear_document_form()
            self._refresh_documents()
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", str(e))

    def _update_document(self) -> None:
        doc_id = self.doc_id_input.text().strip()
        if not doc_id:
            QMessageBox.warning(self, "Missing ID", "Enter a Document ID to update (click a row to load it).")
            return

        title = self.doc_title_input.text().strip() or None
        content = self.doc_content_input.toPlainText().strip() or None

        if documents.update_document(doc_id, title, content):
            QMessageBox.information(self, "Success", "Document updated.")
            self._clear_document_form()
            self._refresh_documents()
        else:
            QMessageBox.critical(self, "Error", "Document not found.")

    def _delete_document(self) -> None:
        doc_id = self.doc_id_input.text().strip()
        if not doc_id:
            QMessageBox.warning(self, "Missing ID", "Enter a Document ID to delete (click a row to load it).")
            return

        confirm = QMessageBox.question(
            self, "Confirm Delete", f"Delete document {doc_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            if documents.delete_document(doc_id):
                QMessageBox.information(self, "Deleted", "Document deleted.")
                self._clear_document_form()
                self._refresh_documents()
            else:
                QMessageBox.critical(self, "Error", "Document not found.")



    def _clear_document_form(self) -> None:
        self.doc_id_input.clear()
        self.doc_title_input.clear()
        self.doc_content_input.clear()

    # ---------------- Steganography Tab ----------------

    def _build_stego_tab(self) -> QWidget:
        tab = QWidget()

        # 👉 Main layout
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 👉 Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        # 👉 Container inside scroll
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # ---------------- Encode Section ----------------
        encode_box = QGroupBox("Hide Message in Image")
        encode_layout = QFormLayout()

        self.stego_image_path = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_image)

        image_row = QHBoxLayout()
        image_row.addWidget(self.stego_image_path)
        image_row.addWidget(browse_btn)

        self.stego_message_input = QTextEdit()
        self.stego_message_input.setFixedHeight(80)

        encode_btn = QPushButton("Encode & Save as encoded.png")
        encode_btn.clicked.connect(self._handle_encode)

        encode_layout.addRow("Image path:", image_row)
        encode_layout.addRow("Secret message:", self.stego_message_input)
        encode_layout.addRow(encode_btn)

        encode_box.setLayout(encode_layout)

        # ---------------- Decode Section ----------------
        decode_box = QGroupBox("Extract Message from Image")
        decode_layout = QFormLayout()

        self.decode_image_path = QLineEdit()
        decode_browse_btn = QPushButton("Browse...")
        decode_browse_btn.clicked.connect(self._browse_decode_image)

        decode_row = QHBoxLayout()
        decode_row.addWidget(self.decode_image_path)
        decode_row.addWidget(decode_browse_btn)

        self.decode_output = QTextEdit()
        self.decode_output.setFixedHeight(80)
        self.decode_output.setReadOnly(True)

        decode_btn = QPushButton("Decode")
        decode_btn.clicked.connect(self._handle_decode)

        decode_layout.addRow("Encoded image path:", decode_row)
        decode_layout.addRow(decode_btn)
        decode_layout.addRow("Hidden message:", self.decode_output)

        decode_box.setLayout(decode_layout)

        # 👉 Add sections
        layout.addWidget(encode_box)
        layout.addWidget(decode_box)
        layout.addStretch()  # 👈 keeps spacing clean

        # 👉 Set scroll content
        scroll.setWidget(container)

        # 👉 Add to tab
        main_layout.addWidget(scroll)

        return tab
    def _browse_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.stego_image_path.setText(path)

    def _browse_decode_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Encoded Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.decode_image_path.setText(path)

    def _handle_encode(self) -> None:
        img_path = self.stego_image_path.text().strip()
        message = self.stego_message_input.toPlainText().strip()

        if not img_path or not message:
            QMessageBox.warning(self, "Missing Fields", "Provide both an image and a message.")
            return

        try:
            encode_image(img_path, message)
            QMessageBox.information(self, "Success", "Message hidden successfully in 'encoded.png'.")
        except (FileNotFoundError, ValueError) as e:
            QMessageBox.critical(self, "Error", str(e))

    def _handle_decode(self) -> None:
        img_path = self.decode_image_path.text().strip()

        if not img_path:
            QMessageBox.warning(self, "Missing Field", "Provide an encoded image path.")
            return

        try:
            # decode_image() prints to console; capture logic ourselves instead
            from PIL import Image
            from stego import DELIMITER

            img = Image.open(img_path).convert("RGB")
            pixels = list(img.getdata())
            binary_data = ""
            for r, g, b in pixels:
                binary_data += str(r & 1) + str(g & 1) + str(b & 1)

            bytes_list = [binary_data[i:i + 8] for i in range(0, len(binary_data), 8)]
            message = ""
            for byte in bytes_list:
                if byte == DELIMITER:
                    break
                message += chr(int(byte, 2))

            self.decode_output.setPlainText(message)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "Image file not found.")

    # ---------------- Password Tools Tab ----------------

    def _build_password_tab(self) -> QWidget:
        tab = QWidget()

        # 👉 Main layout for tab
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 👉 Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        # 👉 Container inside scroll
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # ---------------- Strength Checker ----------------
        strength_box = QGroupBox("Password Strength Checker")
        strength_layout = QFormLayout()

        self.pw_check_input = QLineEdit()
        self.pw_check_input.setEchoMode(QLineEdit.Password)

        self.pw_strength_result = QLabel("")
        self.pw_check_input.textChanged.connect(self._check_password_strength)

        strength_layout.addRow("Password:", self.pw_check_input)
        strength_layout.addRow("Result:", self.pw_strength_result)
        strength_box.setLayout(strength_layout)

        # ---------------- Generator ----------------
        gen_box = QGroupBox("Generate Strong Password")
        gen_layout = QFormLayout()

        self.pw_length_input = QSpinBox()
        self.pw_length_input.setRange(4, 64)
        self.pw_length_input.setValue(12)

        self.pw_generated_output = QLineEdit()
        self.pw_generated_output.setReadOnly(True)

        gen_btn = QPushButton("Generate")
        gen_btn.clicked.connect(self._generate_password)

        gen_layout.addRow("Length:", self.pw_length_input)
        gen_layout.addRow(gen_btn)
        gen_layout.addRow("Generated:", self.pw_generated_output)
        gen_box.setLayout(gen_layout)

        # ---------------- Hash Generator ----------------
        hash_box = QGroupBox("Hash Generator")
        hash_layout = QFormLayout()

        self.hash_text_input = QLineEdit()

        self.hash_algo_combo = QComboBox()
        self.hash_algo_combo.addItems(["sha256", "sha512", "md5"])

        self.hash_output = QLineEdit()
        self.hash_output.setReadOnly(True)

        hash_btn = QPushButton("Generate Hash")
        hash_btn.clicked.connect(self._generate_hash)

        hash_layout.addRow("Text:", self.hash_text_input)
        hash_layout.addRow("Algorithm:", self.hash_algo_combo)
        hash_layout.addRow(hash_btn)
        hash_layout.addRow("Hash:", self.hash_output)
        hash_box.setLayout(hash_layout)

        # 👉 Add all sections
        layout.addWidget(strength_box)
        layout.addWidget(gen_box)
        layout.addWidget(hash_box)
        layout.addStretch()  # 👈 important for clean spacing

        # 👉 Set scroll content
        scroll.setWidget(container)

        # 👉 Add scroll to tab
        main_layout.addWidget(scroll)

        return tab

    def _check_password_strength(self, text: str) -> None:
        if not text:
            self.pw_strength_result.setText("")
            return
        rating, missing = password_tools.check_strength(text)
        color = {"Weak": "red", "Moderate": "orange", "Strong": "green"}.get(rating, "black")
        detail = f"{rating}" + (f" (missing: {', '.join(missing)})" if missing else "")
        self.pw_strength_result.setText(detail)
        self.pw_strength_result.setStyleSheet(f"color: {color};")

    def _generate_password(self) -> None:
        length = self.pw_length_input.value()
        pwd = password_tools.generate_password(length)
        self.pw_generated_output.setText(pwd)

    def _generate_hash(self) -> None:
        text = self.hash_text_input.text().strip()
        algo = self.hash_algo_combo.currentText()
        if not text:
            QMessageBox.warning(self, "Missing Text", "Enter text to hash.")
            return
        result = password_tools.hash_text(text, algo)
        self.hash_output.setText(result)

    # ---------------- Report Tab ----------------

    def _build_report_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout()

        self.report_output = QTextEdit()
        self.report_output.setReadOnly(True)

        refresh_btn = QPushButton("Generate / Refresh Report")
        refresh_btn.clicked.connect(self._generate_report)

        layout.addWidget(refresh_btn)
        layout.addWidget(self.report_output)
        tab.setLayout(layout)

        self._generate_report()
        return tab

    def _generate_report(self) -> None:
        users = auth.list_users()
        docs = documents.list_documents()

        owner_counts = {}
        for doc in docs.values():
            owner_counts[doc["owner"]] = owner_counts.get(doc["owner"], 0) + 1

        lines = [
            "SYSTEM REPORT",
            "=" * 40,
            f"Total registered users : {len(users)}",
            f"Total documents stored : {len(docs)}",
            "",
            "Documents by owner:",
        ]
        for owner, count in owner_counts.items():
            lines.append(f"  {owner}: {count} document(s)")

        self.report_output.setPlainText("\n".join(lines))

    # ---------------- Logout ----------------

    def _handle_logout(self) -> None:
        self.close()
        self.on_logout()