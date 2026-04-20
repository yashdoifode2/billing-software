import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Test")
window.setGeometry(100, 100, 400, 300)
label = QLabel("Hello World!", window)
label.move(150, 140)
window.show()
print("Window should be visible")
print("If you don't see a window, there might be display issues")
sys.exit(app.exec_())