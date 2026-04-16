import os
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy,
    QToolButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QIcon
from core.extension import WallpaperExtension
from core.workers import ThumbnailLoader


THUMB_SIZE = QSize(280, 158)


class WallpaperWidget(QFrame):
    download_triggered = pyqtSignal(dict)
    expand_triggered = pyqtSignal(dict)  # New signal for the expand feature

    def __init__(self, extension: WallpaperExtension, wallpaper_data: dict, download_folder: str, parent=None):
        super().__init__(parent)
        self.extension = extension
        self.data = wallpaper_data
        self.download_folder = download_folder
        self.thumb_url = extension.get_thumbnail_url(wallpaper_data)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            WallpaperWidget {
                background-color: #2d2d2d;
                border-radius: 8px;
            }
            WallpaperWidget:hover {
                background-color: #3d3d3d;
            }
        """)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.init_ui()
        self.load_thumbnail()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Thumbnail label
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(THUMB_SIZE)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border-radius: 6px;
            }
            QLabel:hover {
                border: 2px solid #1E6FF0;
            }
        """)
        self.thumb_label.setScaledContents(True)
        self.thumb_label.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.thumb_label, alignment=Qt.AlignHCenter)

        # Spacer for separation
        layout.addStretch()

        # ========== SINGLE BOTTOM ROW ==========
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(16)

        # Checkmark (leftmost)
        self.checkmark_label = QLabel()
        self.checkmark_label.setAlignment(Qt.AlignCenter)
        self.checkmark_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 180, 0, 0.85);
                color: white;
                font-weight: bold;
                font-size: 12px;
                border-radius: 4px;
                padding: 2px 12px;
            }
        """)
        self.checkmark_label.setText("✓")
        self.checkmark_label.hide()
        bottom_layout.addWidget(self.checkmark_label)

        # Resolution
        res = self.extension.get_resolution(self.data)
        self.res_label = QLabel(res)
        self.res_label.setStyleSheet("color: #aaa; font-size: 12px;")
        bottom_layout.addWidget(self.res_label)

        bottom_layout.addStretch()

        # Expand button (REPLACES download button)
        self.expand_btn = QToolButton()
        self.expand_btn.setText("⤢")  # Symbol for expand
        self.expand_btn.setToolTip("Expand Preview")
        self.expand_btn.setCursor(Qt.PointingHandCursor)
        self.expand_btn.setStyleSheet("""
            QToolButton {
                background-color: rgba(60, 60, 60, 0.8);
                border-radius: 4px;
                padding: 4px;
                border: none;
                color: white;
                font-size: 14px;
            }
            QToolButton:hover {
                background-color: rgba(80, 80, 80, 1);
            }
        """)
        self.expand_btn.clicked.connect(lambda: self.expand_triggered.emit(self.data))
        bottom_layout.addWidget(self.expand_btn)

        layout.addLayout(bottom_layout)

        self.setLayout(layout)
        self.setFixedSize(THUMB_SIZE.width() + 20, THUMB_SIZE.height() + 54)

    def mouseDoubleClickEvent(self, event):
        """Triggers download on double click."""
        if event.button() == Qt.LeftButton:
            self.emit_download()

    def showEvent(self, event):
        super().showEvent(event)
        self.update_downloaded_status()

    def update_downloaded_status(self):
        wall_id = self.extension.get_wallpaper_id(self.data)
        ext = self.extension.get_file_extension(self.data)
        filename = f"wallppy-{wall_id}.{ext}"
        filepath = os.path.join(self.download_folder, filename)
        if os.path.exists(filepath):
            self.checkmark_label.show()
        else:
            self.checkmark_label.hide()

    def load_thumbnail(self):
        if self.thumb_url:
            self.loader = ThumbnailLoader(self.thumb_url)
            self.loader.loaded.connect(self.set_thumbnail)
            self.loader.start()
        else:
            self.thumb_label.setText("No preview")

    def set_thumbnail(self, pixmap: QPixmap):
        if not pixmap.isNull():
            scaled = pixmap.scaled(THUMB_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.thumb_label.setPixmap(scaled)
        else:
            self.thumb_label.setText("Load failed")
        self.update_downloaded_status()

    def emit_download(self):
        self.download_triggered.emit(self.data)