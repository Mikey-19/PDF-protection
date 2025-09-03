# pdf_protection_gui.py
import sys
import os
import PyPDF2

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QComboBox, QHBoxLayout
)

LIGHT_QSS = """
* { font-family: 'Segoe UI', sans-serif; }
QWidget { background: #f7f7fb; color: #202124; }
QLineEdit, QGroupBox { background: white; border: 1px solid #d0d3d8; border-radius: 8px; padding: 6px; }
QPushButton { background: #1a73e8; color: white; border: none; padding: 8px 12px; border-radius: 10px; }
QPushButton:hover { background: #1669c1; }
QPushButton:disabled { background: #9bb7e6; }
QGroupBox { border: 1px solid #d0d3d8; margin-top: 10px; padding-top: 12px; }
"""

DARK_QSS = """
* { font-family: 'Segoe UI', sans-serif; }
QWidget { background: #0f1218; color: #e6e8ee; }
QLineEdit, QGroupBox { background: #171b22; border: 1px solid #2a2f3a; border-radius: 8px; padding: 6px; color: #e6e8ee; }
QPushButton { background: #3b82f6; color: white; border: none; padding: 8px 12px; border-radius: 10px; }
QPushButton:hover { background: #2563eb; }
QPushButton:disabled { background: #27344d; }
QGroupBox { border: 1px solid #2a2f3a; margin-top: 10px; padding-top: 12px; }
"""


class PDFApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Protection — GUI")
        self._dark = True
        self._build_ui()
        self._apply_theme()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        box = QGroupBox("Protect a PDF with a Password")
        grid = QGridLayout(box)

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Select input PDF...")
        self.in_browse = QPushButton("Browse")

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Output file (e.g., output_protected.pdf)")
        self.out_browse = QPushButton("Browse")

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Password")

        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit.setPlaceholderText("Confirm password")

        self.theme_toggle = QComboBox()
        self.theme_toggle.addItems(["Dark", "Light"])
        self.theme_toggle.currentIndexChanged.connect(self._toggle_theme)

        self.protect_btn = QPushButton("Protect PDF")

        grid.addWidget(QLabel("Input PDF"), 0, 0)
        grid.addWidget(self.input_edit, 0, 1)
        grid.addWidget(self.in_browse, 0, 2)

        grid.addWidget(QLabel("Output PDF"), 1, 0)
        grid.addWidget(self.output_edit, 1, 1)
        grid.addWidget(self.out_browse, 1, 2)

        grid.addWidget(QLabel("Password"), 2, 0)
        grid.addWidget(self.password_edit, 2, 1)

        grid.addWidget(QLabel("Confirm"), 3, 0)
        grid.addWidget(self.confirm_edit, 3, 1)

        grid.addWidget(QLabel("Theme"), 4, 0)
        grid.addWidget(self.theme_toggle, 4, 1)

        layout.addWidget(box)
        layout.addWidget(self.protect_btn)

        # Hooks
        self.in_browse.clicked.connect(self._pick_input)
        self.out_browse.clicked.connect(self._pick_output)
        self.protect_btn.clicked.connect(self._protect)

    def _toggle_theme(self):
        self._dark = (self.theme_toggle.currentText() == "Dark")
        self._apply_theme()

    def _apply_theme(self):
        self.setStyleSheet(DARK_QSS if self._dark else LIGHT_QSS)

    def _pick_input(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if path:
            self.input_edit.setText(path)
            if not self.output_edit.text().strip():
                base = os.path.splitext(os.path.basename(path))[0]
                self.output_edit.setText(os.path.join(os.path.dirname(path), f"{base}_protected.pdf"))

    def _pick_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "output_protected.pdf", "PDF Files (*.pdf)")
        if path:
            if not path.lower().endswith(".pdf"):
                path += ".pdf"
            self.output_edit.setText(path)

    def _protect(self):
        in_path = self.input_edit.text().strip()
        out_path = self.output_edit.text().strip()
        pwd = self.password_edit.text()
        confirm = self.confirm_edit.text()

        if not in_path or not os.path.isfile(in_path):
            QMessageBox.warning(self, "Validation", "Please choose a valid input PDF.")
            return
        if not out_path:
            QMessageBox.warning(self, "Validation", "Please choose an output filename.")
            return
        if not pwd:
            QMessageBox.warning(self, "Validation", "Password cannot be empty.")
            return
        if pwd != confirm:
            QMessageBox.warning(self, "Validation", "Passwords do not match.")
            return

        try:
            with open(in_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                writer = PyPDF2.PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)

                # Basic user-password encryption (owner password = same for simplicity)
                writer.encrypt(user_password=pwd, owner_password=pwd)

                with open(out_path, "wb") as out:
                    writer.write(out)

            QMessageBox.information(self, "Success", f"Password-protected PDF saved:\n{out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to protect PDF:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PDFApp()
    w.resize(600, 260)
    w.show()
    sys.exit(app.exec_())
