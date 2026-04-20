from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import base64
import os

class LogoUploadDialog(QDialog):
    def __init__(self, current_logo=None, parent=None):
        super().__init__(parent)
        self.current_logo = current_logo
        self.logo_data = None
        self.setup_ui()
        self.setWindowTitle("Upload Business Logo")
        self.setModal(True)
        self.setFixedSize(500, 400)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Business Logo")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Logo preview
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(300, 200)
        self.preview_label.setStyleSheet("""
            border: 2px dashed #bdc3c7;
            border-radius: 10px;
            background-color: #f8f9fa;
        """)
        self.preview_label.setScaledContents(True)
        
        if self.current_logo:
            try:
                pixmap = QPixmap()
                pixmap.loadFromData(base64.b64decode(self.current_logo))
                scaled_pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_label.setPixmap(scaled_pixmap)
            except:
                self.preview_label.setText("No Logo\n\nClick 'Select Logo' to upload")
        else:
            self.preview_label.setText("No Logo\n\nClick 'Select Logo' to upload")
        
        layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.select_btn = QPushButton("📁 Select Logo")
        self.select_btn.setMinimumHeight(40)
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.select_btn.clicked.connect(self.select_logo)
        button_layout.addWidget(self.select_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear Logo")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_logo)
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        # Info label
        info_label = QLabel("Supported formats: PNG, JPG, JPEG (Max size: 2MB)\nRecommended size: 200x200 pixels")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Dialog buttons
        dialog_buttons = QHBoxLayout()
        self.save_btn = QPushButton("Save Logo")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.clicked.connect(self.reject)
        
        dialog_buttons.addWidget(self.save_btn)
        dialog_buttons.addWidget(self.cancel_btn)
        layout.addLayout(dialog_buttons)
    
    def select_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Logo", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            # Check file size (max 2MB)
            file_size = os.path.getsize(file_path)
            if file_size > 2 * 1024 * 1024:
                QMessageBox.warning(self, "File Too Large", "Logo file size should be less than 2MB!")
                return
            
            # Load and display image
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
            
            # Convert to base64
            with open(file_path, 'rb') as f:
                self.logo_data = base64.b64encode(f.read()).decode('utf-8')
    
    def clear_logo(self):
        self.logo_data = None
        self.preview_label.setText("No Logo\n\nClick 'Select Logo' to upload")
        self.preview_label.setPixmap(QPixmap())
    
    def get_logo_data(self):
        return self.logo_data