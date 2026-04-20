import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from views.main_window import MainWindow

def main():
    # Set high DPI attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Create resources directory if not exists
    if not os.path.exists('resources'):
        os.makedirs('resources')
    
    # Create default stylesheet if not exists
    if not os.path.exists('resources/styles.qss'):
        with open('resources/styles.qss', 'w') as f:
            f.write("""
                QMainWindow {
                    background-color: #f5f5f5;
                }
                
                #sidebar {
                    background-color: #2c3e50;
                    border-right: 1px solid #34495e;
                }
                
                #sidebar_title {
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 10px;
                }
                
                QListWidget#nav_button {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-size: 14px;
                }
                
                QListWidget#nav_button:hover {
                    background-color: #34495e;
                }
                
                QListWidget#nav_button:selected {
                    background-color: #3498db;
                }
                
                #page_title {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 20px;
                }
                
                #stat_card {
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                    min-width: 200px;
                }
                
                #stat_title {
                    color: #7f8c8d;
                    font-size: 14px;
                }
                
                #stat_value {
                    color: #2c3e50;
                    font-size: 28px;
                    font-weight: bold;
                }
                
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
                
                QPushButton:pressed {
                    background-color: #21618c;
                }
                
                QLineEdit, QTextEdit, QComboBox {
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 14px;
                }
                
                QLineEdit:focus, QTextEdit:focus {
                    border-color: #3498db;
                }
                
                QTableWidget {
                    background-color: white;
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                }
                
                QTableWidget::item {
                    padding: 8px;
                }
                
                QHeaderView::section {
                    background-color: #ecf0f1;
                    padding: 8px;
                    border: none;
                    font-weight: bold;
                }
                
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()