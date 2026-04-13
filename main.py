#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from core.settings import Settings
from extensions.wallhaven import WallhavenExtension
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon.fromTheme("wallpaper"))
    
    settings = Settings()
    extension = WallhavenExtension()  # Could be selected via config later
    
    window = MainWindow(extension, settings)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()