import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QCheckBox, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from core.settings import Settings


class LandingPage(QWidget):
    search_requested = pyqtSignal(str)
    
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        search_container = QWidget()
        search_container.setFixedWidth(550)
        container_layout = QVBoxLayout(search_container)
        container_layout.setSpacing(15)
        
        title = QLabel("wallppy")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #1E6FF0;")
        container_layout.addWidget(title)
        
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
        
        hint1 = QLabel("Press Enter to search")
        hint1.setAlignment(Qt.AlignCenter)
        hint1.setStyleSheet("color: #777; font-size: 12px;")
        container_layout.addWidget(hint1)
        
        # Categories
        filter_label = QLabel("Categories")
        filter_label.setStyleSheet("color: #aaa; font-size: 13px; font-weight: bold; margin-top: 5px;")
        container_layout.addWidget(filter_label)
        
        cat_layout = QHBoxLayout()
        cat_layout.setSpacing(20)
        cat_layout.setAlignment(Qt.AlignCenter)
        
        self.cat_general = QCheckBox("General")
        self.cat_anime = QCheckBox("Anime")
        self.cat_people = QCheckBox("People")
        
        self.cat_general.setChecked(self.settings.categories["general"])
        self.cat_anime.setChecked(self.settings.categories["anime"])
        self.cat_people.setChecked(self.settings.categories["people"])
        
        self.cat_general.stateChanged.connect(self.save_categories)
        self.cat_anime.stateChanged.connect(self.save_categories)
        self.cat_people.stateChanged.connect(self.save_categories)
        
        cat_layout.addWidget(self.cat_general)
        cat_layout.addWidget(self.cat_anime)
        cat_layout.addWidget(self.cat_people)
        container_layout.addLayout(cat_layout)
        
        # Purity
        purity_label = QLabel("Content")
        purity_label.setStyleSheet("color: #aaa; font-size: 13px; font-weight: bold; margin-top: 5px;")
        container_layout.addWidget(purity_label)
        
        purity_layout = QHBoxLayout()
        purity_layout.setSpacing(20)
        purity_layout.setAlignment(Qt.AlignCenter)
        
        self.purity_sfw = QCheckBox("SFW")
        self.purity_sketchy = QCheckBox("Sketchy")
        
        self.purity_sfw.setChecked(self.settings.purity["sfw"])
        self.purity_sketchy.setChecked(self.settings.purity["sketchy"])
        
        self.purity_sfw.stateChanged.connect(self.save_purity)
        self.purity_sketchy.stateChanged.connect(self.save_purity)
        
        purity_layout.addWidget(self.purity_sfw)
        purity_layout.addWidget(self.purity_sketchy)
        container_layout.addLayout(purity_layout)
        
        # Directory
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
        
        layout.addWidget(search_container)
    
    def emit_search(self):
        query = self.search_edit.text().strip()
        if query:
            self.search_requested.emit(query)
    
    def get_category_string(self):
        cat = ""
        cat += "1" if self.cat_general.isChecked() else "0"
        cat += "1" if self.cat_anime.isChecked() else "0"
        cat += "1" if self.cat_people.isChecked() else "0"
        return cat
    
    def get_purity_string(self):
        purity = ""
        purity += "1" if self.purity_sfw.isChecked() else "0"
        purity += "1" if self.purity_sketchy.isChecked() else "0"
        purity += "0"
        return purity
    
    def save_categories(self):
        self.settings.set_categories(
            self.cat_general.isChecked(),
            self.cat_anime.isChecked(),
            self.cat_people.isChecked()
        )
    
    def save_purity(self):
        self.settings.set_purity(
            self.purity_sfw.isChecked(),
            self.purity_sketchy.isChecked()
        )
    
    def choose_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.settings.download_folder)
        if folder:
            self.settings.set_download_folder(folder)
            self.dir_edit.setText(folder)
    
    def set_search_text(self, text: str):
        self.search_edit.setText(text)