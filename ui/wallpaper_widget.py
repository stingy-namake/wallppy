import os
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QMouseEvent
from core.extension import WallpaperExtension
from core.workers import ThumbnailLoader


THUMB_SIZE = QSize(280, 158)


class DoubleClickableLabel(QLabel):
    double_clicked = pyqtSignal()
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)


class WallpaperWidget(QFrame):
    download_triggered = pyqtSignal(dict)
    
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
        
        self.thumb_label = DoubleClickableLabel()
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
        self.thumb_label.double_clicked.connect(self.emit_download)
        layout.addWidget(self.thumb_label)
        
        self.checkmark_label = QLabel(self.thumb_label)
        self.checkmark_label.setAlignment(Qt.AlignCenter)
        self.checkmark_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 180, 0, 0.85);
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 4px;
                padding: 2px 6px;
            }
        """)
        self.checkmark_label.setText("✓")
        self.checkmark_label.hide()
        self.checkmark_label.raise_()
        
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        res = self.extension.get_resolution(self.data)
        self.res_label = QLabel(res)
        self.res_label.setStyleSheet("color: #aaa; font-size: 10px;")
        info_layout.addWidget(self.res_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        self.setLayout(layout)
        self.setFixedSize(THUMB_SIZE.width() + 20, THUMB_SIZE.height() + 45)
    
    def showEvent(self, event):
        super().showEvent(event)
        self.position_checkmark()
        self.update_downloaded_status()
    
    def position_checkmark(self):
        if self.checkmark_label:
            label_width = self.checkmark_label.sizeHint().width()
            label_height = self.checkmark_label.sizeHint().height()
            margin = 4
            self.checkmark_label.move(
                THUMB_SIZE.width() - label_width - margin,
                THUMB_SIZE.height() - label_height - margin
            )
    
    def update_downloaded_status(self):
        wall_id = self.extension.get_wallpaper_id(self.data)
        ext = self.extension.get_file_extension(self.data)
        filename = f"wallppy-{wall_id}.{ext}"
        filepath = os.path.join(self.download_folder, filename)
        if os.path.exists(filepath):
            self.checkmark_label.show()
            self.checkmark_label.raise_()
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
        self.position_checkmark()
        self.update_downloaded_status()
    
    def emit_download(self):
        self.download_triggered.emit(self.data)