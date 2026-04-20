from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QComboBox, QFileDialog,
                             QMessageBox, QDateEdit, QGroupBox)
from PyQt5.QtCore import Qt, QDate
import os
from datetime import datetime, timedelta

class LogViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Logs Viewer")
        self.setModal(True)
        self.resize(900, 600)
        self.setup_ui()
        self.load_logs()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("System Logs Viewer")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Filter controls
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Log Type:"))
        self.log_type = QComboBox()
        self.log_type.addItems(["app", "error", "database", "user_activity", "performance", "security"])
        self.log_type.currentTextChanged.connect(self.load_logs)
        filter_layout.addWidget(self.log_type)
        
        filter_layout.addWidget(QLabel("Lines:"))
        self.lines_count = QComboBox()
        self.lines_count.addItems(["100", "500", "1000", "All"])
        self.lines_count.currentTextChanged.connect(self.load_logs)
        filter_layout.addWidget(self.lines_count)
        
        filter_layout.addStretch()
        
        layout.addWidget(filter_group)
        
        # Log display area
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Monospace';
                font-size: 11px;
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.log_display)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_logs)
        button_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("🗑️ Clear Display")
        clear_btn.clicked.connect(self.clear_display)
        button_layout.addWidget(clear_btn)
        
        export_btn = QPushButton("💾 Export Logs")
        export_btn.clicked.connect(self.export_logs)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_logs(self):
        log_type = self.log_type.currentText()
        lines = self.lines_count.currentText()
        
        log_file_map = {
            "app": "app.log",
            "error": "error.log",
            "database": "database.log",
            "user_activity": "user_activity.log",
            "performance": "performance.log",
            "security": "security.log"
        }
        
        log_file = log_file_map.get(log_type, "app.log")
        log_path = os.path.join("logs", log_file)
        
        if not os.path.exists(log_path):
            self.log_display.setText(f"No log file found: {log_file}")
            return
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                
                if lines != "All":
                    max_lines = int(lines)
                    recent_lines = all_lines[-max_lines:]
                else:
                    recent_lines = all_lines
                
                self.log_display.setText(''.join(recent_lines))
                
                # Scroll to bottom
                cursor = self.log_display.textCursor()
                cursor.movePosition(cursor.End)
                self.log_display.setTextCursor(cursor)
                
        except Exception as e:
            self.log_display.setText(f"Error reading log file: {str(e)}")
    
    def clear_display(self):
        self.log_display.clear()
    
    def export_logs(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_display.toPlainText())
                QMessageBox.information(self, "Success", f"Logs exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export logs: {str(e)}")