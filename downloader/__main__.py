import sys

from PyQt5.QtWidgets import QApplication

from downloader.ui.main_window import MainWindow

qss = """
    QMenuBar {
        background-color: transparent;
    }
"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qss)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
