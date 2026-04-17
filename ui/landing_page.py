import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from core.settings import Settings
from core.extension import get_extension_names


class LandingPage(QWidget):
    search_requested = pyqtSignal(str)
    explore_requested = pyqtSignal()  # New signal
    extension_changed = pyqtSignal(str)
    
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        container = QWidget()
        container.setFixedWidth(550)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        
        title = QLabel("wallppy")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #1E6FF0;")
        container_layout.addWidget(title)
        
        # Source selector
        src_layout = QHBoxLayout()
        src_layout.setSpacing(10)
        src_label = QLabel("Source:")
        src_label.setStyleSheet("color: #aaa; font-size: 13px;")
        self.ext_combo = QComboBox()
        self.ext_combo.addItems(get_extension_names())
        self.ext_combo.setCurrentText(self.settings.extension_name)
        self.ext_combo.currentTextChanged.connect(self.on_extension_changed)
        src_layout.addWidget(src_label)
        src_layout.addWidget(self.ext_combo)
        src_layout.addStretch()
        container_layout.addLayout(src_layout)
        
        # Search input
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search wallpapers...")
        self.search_edit.setMinimumHeight(50)
        self.search_edit.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 12px;
                border-radius: 25px;
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #1E6FF0;
            }
        """)
        self.search_edit.returnPressed.connect(self.emit_search)
        container_layout.addWidget(self.search_edit)
        
        # Hint and Explore button row
        hint_layout = QHBoxLayout()
        hint_layout.setSpacing(10)
        
        hint = QLabel("Press Enter to search")
        hint.setAlignment(Qt.AlignLeft)
        hint.setStyleSheet("color: #777; font-size: 12px;")
        hint_layout.addWidget(hint)
        
        hint_layout.addStretch()
        
        self.explore_btn = QPushButton("Explore")
        self.explore_btn.setToolTip("Browse recent uploads")
        self.explore_btn.setFixedHeight(32)
        self.explore_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #3d3d3d;
                border-radius: 16px;
                padding: 6px 16px;
                color: #aaa;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                color: white;
            }
        """)
        self.explore_btn.clicked.connect(self.emit_explore)
        hint_layout.addWidget(self.explore_btn)
        
        container_layout.addLayout(hint_layout)
        
        # Directory chooser
        dir_label = QLabel("Save to")
        dir_label.setStyleSheet("color: #aaa; font-size: 13px; font-weight: bold; margin-top: 10px;")
        container_layout.addWidget(dir_label)
        
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(10)
        
        self.dir_edit = QLineEdit()
        self.dir_edit.setText(self.settings.download_folder)
        self.dir_edit.setReadOnly(True)
        dir_layout.addWidget(self.dir_edit)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.clicked.connect(self.choose_directory)
        dir_layout.addWidget(self.browse_btn)
        
        container_layout.addLayout(dir_layout)
        
        layout.addWidget(container)
    
    def emit_search(self):
        query = self.search_edit.text().strip()
        if query:
            self.search_requested.emit(query)
    
    def emit_explore(self):
        """Emit signal for explore action (empty query)."""
        self.explore_requested.emit()
    
    def on_extension_changed(self, name: str):
        self.settings.set_extension(name)
        self.extension_changed.emit(name)
    
    def choose_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.settings.download_folder)
        if folder:
            self.settings.set_download_folder(folder)
            self.dir_edit.setText(folder)
    
    def set_search_text(self, text: str):
        self.search_edit.setText(text)