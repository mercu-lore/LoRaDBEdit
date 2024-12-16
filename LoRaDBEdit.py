import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, 
    QSizePolicy, QTextEdit, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QSize
from PIL import Image

class ImageTextEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LoRa DB Edit")
        self.setGeometry(100, 100, 800, 600)

        # Image and file tracking variables
        self.image_files = []
        self.text_files = {}
        self.current_index = 0
        self.current_folder = ""
        self.original_image_size = (0, 0)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Image section
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.image_label)

        # Image info section
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 10, 0, 10)
        info_layout.setSpacing(10)

        # Info groups
        self.resolution_group = self._create_info_group("Resolution", "")
        self.image_name_group = self._create_info_group("Image Name", "")
        self.page_group = self._create_info_group("Page", "")

        info_layout.addStretch(1)
        info_layout.addLayout(self.resolution_group)
        info_layout.addLayout(self.image_name_group)
        info_layout.addLayout(self.page_group)
        info_layout.addStretch(1)

        main_layout.addLayout(info_layout)

        # Text edit section
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("Enter your text here...")
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.text_edit)

        # Button section
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 10)
        button_layout.setSpacing(10)

        # Previous Button (Red)
        self.prev_button = QPushButton("Previous", self)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #FF0000;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 10px 20px;
                min-width: 120px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #CC0000;
            }
        """)
        self.prev_button.clicked.connect(self.prev_image)

        # Load Image Button (Blue)
        self.load_button = QPushButton("Load Images", self)
        self.load_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 10px 20px;
                min-width: 120px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.load_button.clicked.connect(self.load_images)

        # Next Button (Green)
        self.next_button = QPushButton("Next", self)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 10px 20px;
                min-width: 120px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.next_button.clicked.connect(self.next_image)

        # Manually Save Button (Yellow)
        self.save_button = QPushButton("Save Text", self)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                color: black;
                border: none;
                border-radius: 25px;
                padding: 10px 20px;
                min-width: 120px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFD54F;
            }
        """)
        self.save_button.clicked.connect(self.save_text)

        # Button Layout in a single row
        button_layout.addStretch(1)
        button_layout.addWidget(self.prev_button)  # Red button
        button_layout.addWidget(self.load_button)  # Blue button
        button_layout.addWidget(self.save_button)  # Yellow button
        button_layout.addWidget(self.next_button)  # Green button
        button_layout.addStretch(1)

        main_layout.addLayout(button_layout)

        # Set main layout
        self.setLayout(main_layout)

        # Disable navigation buttons initially
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.save_button.setEnabled(False)

    def _create_info_group(self, label_text, value_text):
        """
        Create a vertical group with a label on top and a value below.
        """
        group_layout = QVBoxLayout()
        group_layout.setSpacing(5)

        label = QLabel(label_text)
        label.setStyleSheet("""
            font-weight: bold; 
            margin-bottom: 5px; 
            color: #333;
        """)
        label.setAlignment(Qt.AlignCenter)

        value = QLabel(value_text)
        value.setStyleSheet("""
            background-color: white; 
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 5px;
            min-width: 100px;
            text-align: center;
        """)
        value.setAlignment(Qt.AlignCenter)

        group_layout.addWidget(label)
        group_layout.addWidget(value)

        return group_layout

    def load_images(self):
        """
        Load images from a selected folder
        """
        self.current_folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if not self.current_folder:
            return

        # Find image and text files
        self.image_files = sorted([f for f in os.listdir(self.current_folder) 
                            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))])
        
        self.text_files = {}
        for img in self.image_files:
            base_name = os.path.splitext(img)[0]
            txt_file = base_name + ".txt"
            txt_path = os.path.join(self.current_folder, txt_file)
            if os.path.exists(txt_path):
                self.text_files[base_name] = txt_file
            else:
                # Crea un file di testo vuoto se non esiste
                open(txt_path, 'a').close()
                self.text_files[base_name] = txt_file

        if self.image_files:
            self.current_index = 0
            self.show_image_and_text()

            # Enable/disable navigation buttons
            self.prev_button.setEnabled(len(self.image_files) > 1)
            self.next_button.setEnabled(len(self.image_files) > 1)
            self.save_button.setEnabled(True)

    def show_image_and_text(self):
        """
        Display current image and associated text
        """
        if not self.image_files:
            return

        try:
            # Load and scale image
            image_path = os.path.join(self.current_folder, self.image_files[self.current_index])
            image = Image.open(image_path)
            self.original_image_size = image.size

            # Scale image to fit window
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(self.width() - 40, int(self.height() * 0.5), 
                                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)

            # Update image info
            image_name = self.image_files[self.current_index]
            total_images = len(self.image_files)
            base_name = os.path.splitext(image_name)[0]
            
            # Update resolution label
            resolution_label = self.resolution_group.itemAt(1).widget()
            resolution_label.setText(f"{self.original_image_size[0]} x {self.original_image_size[1]}")

            # Update image name label
            name_label = self.image_name_group.itemAt(1).widget()
            name_label.setText(image_name)

            # Update page/position label
            page_label = self.page_group.itemAt(1).widget()
            page_label.setText(f"{self.current_index + 1} of {total_images}")

            # Load associated text file
            text_content = ""
            txt_path = os.path.join(self.current_folder, base_name + ".txt")
            
            try:
                # Usa 'r+' per aprire in lettura e scrittura senza troncare
                with open(txt_path, 'r+', encoding='utf-8') as file:
                    text_content = file.read()
            except FileNotFoundError:
                # Crea il file se non esiste
                open(txt_path, 'a').close()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not read text file: {e}")

            # Update text edit
            self.text_edit.setPlainText(text_content)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading image: {e}")

    def save_text(self):
        """
        Save the current text to the associated text file
        """
        if not self.image_files:
            return

        base_name = os.path.splitext(self.image_files[self.current_index])[0]
        txt_path = os.path.join(self.current_folder, base_name + ".txt")

        try:
            # Usa 'w' per sovrascrivere, non 'a' per appendere
            with open(txt_path, 'w', encoding='utf-8') as file:
                file.write(self.text_edit.toPlainText())
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save text file: {e}")

    def prev_image(self):
        """
        Navigate to previous image
        """
        if self.current_index > 0:
            # Salva il testo prima di cambiare immagine
            self.save_text()
            self.current_index -= 1
            self.show_image_and_text()

    def next_image(self):
        """
        Navigate to next image
        """
        if self.current_index < len(self.image_files) - 1:
            # Salva il testo prima di cambiare immagine
            self.save_text()
            self.current_index += 1
            self.show_image_and_text()

    def resizeEvent(self, event):
        """
        Resize image when window is resized
        """
        super().resizeEvent(event)

        # Redraw current image if exists
        if self.current_folder and self.image_files:
            self.show_image_and_text()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageTextEditor()
    window.show()
    sys.exit(app.exec_())