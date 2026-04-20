#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.login_dialog import LoginDialog
from views.main_window import MainWindow
from database.db_manager import DatabaseManager
from config import Config

def main():
    print("Starting Professional Invoice System...")
    
    # Set high DPI attributes
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Professional Invoice System")
    
    # Initialize database
    print("Initializing database...")
    db = DatabaseManager(Config.DATABASE_PATH)
    
    # Show login dialog
    login_dialog = LoginDialog()
    
    def on_login_success(user):
        print(f"Login successful: {user['username']}")
        main_window = MainWindow(user)
        main_window.show()
        login_dialog.close()
    
    login_dialog.login_successful.connect(on_login_success)
    login_dialog.show()
    
    print("Application running...")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()