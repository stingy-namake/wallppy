# ============================================================
# SECTION: Imports & Dependencies
# ============================================================
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QFileDialog, QComboBox, QFrame, QApplication, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QSize
from PyQt5.QtGui import QColor, QFont, QLinearGradient, QPalette

from core.settings import Settings
from core.extension import get_extension_names


# ============================================================
# SECTION: Landing Page Widget
# ============================================================
class LandingPage(QWidget):
    """
    Landing page with modern centered layout.
    Features: Glassmorphism search container, neon accents,
    animated interactions, and improved visual hierarchy.
    """
    
    # Color palette matching main window
    COLOR_BG_PRIMARY = "#050508"
    COLOR_BG_SECONDARY = "#0a0a0c"
    COLOR_BG_TERTIARY = "#1e1e24"
    COLOR_ACCENT_PRIMARY = "#00d4ff"
    COLOR_ACCENT_SECONDARY = "#7b61ff"
    COLOR_TEXT_PRIMARY = "#ffffff"
    COLOR_TEXT_SECONDARY = "#a0a0b0"
    COLOR_TEXT_MUTED = "#6a6a7a"
    COLOR_BORDER = "#2a2a35"
    COLOR_BORDER_HOVER = "#3a3a4a"
    
    # Signals for communication with main window
    search_requested = pyqtSignal(str)
    explore_requested = pyqtSignal()
    extension_changed = pyqtSignal(str)
    status_message = pyqtSignal(str)

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self._search_timer = None
        self.init_ui()
        self.on_extension_changed(self.ext_combo.currentText())

    # ============================================================
    # SECTION: UI Initialization
    # ============================================================
    def init_ui(self):
        """Build the landing page UI with modern styling."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(32)
        layout.setContentsMargins(40, 40, 40, 40)

        # Central container
        container = QWidget()
        container.setFixedWidth(560)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # ============================================================
        # SUBSECTION: Logo / Title
        # ============================================================
        title = QLabel("wallppy")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 48px;
            font-weight: 800;
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {self.COLOR_ACCENT_PRIMARY}, 
                stop:1 {self.COLOR_ACCENT_SECONDARY});
            margin-bottom: 8px;
            background: transparent;
            border: none;
        """)
        container_layout.addWidget(title)

        # ============================================================
        # SUBSECTION: Source Selector
        # ============================================================
        src_layout = QHBoxLayout()
        src_layout.setSpacing(8)
        
        src_label = QLabel("SOURCE")
        src_label.setStyleSheet(f"""
            color: {self.COLOR_TEXT_MUTED}; 
            font-size: 11px; 
            font-weight: 700; 
            letter-spacing: 1.5px;
            background: transparent;
            border: none;
        """)
        
        self.ext_combo = QComboBox()
        self.ext_combo.addItems(get_extension_names())
        self.ext_combo.setCurrentText(self.settings.extension_name)
        self.ext_combo.currentTextChanged.connect(self.on_extension_changed)
        self.ext_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.COLOR_BG_TERTIARY};
                border: 1px solid {self.COLOR_BORDER};
                border-radius: 8px;
                color: {self.COLOR_TEXT_PRIMARY};
                font-size: 13px;
                padding: 6px 12px;
                min-width: 140px;
            }}
            QComboBox:hover {{
                border-color: {self.COLOR_BORDER_HOVER};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.COLOR_ACCENT_PRIMARY};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.COLOR_BG_TERTIARY};
                color: {self.COLOR_TEXT_PRIMARY};
                border: 1px solid {self.COLOR_BORDER};
                border-radius: 8px;
                selection-background-color: {self.COLOR_ACCENT_PRIMARY};
                selection-color: {self.COLOR_BG_PRIMARY};
                padding: 4px;
            }}
        """)
        
        src_layout.addWidget(src_label)
        src_layout.addWidget(self.ext_combo)
        src_layout.addStretch()
        container_layout.addLayout(src_layout)

        # ============================================================
        # SUBSECTION: Search Input Container
        # ============================================================
        search_wrapper = QFrame()
        search_wrapper.setStyleSheet(f"""
            QFrame {{
                background-color: {self.COLOR_BG_TERTIARY};
                border-radius: 12px;
                border: 1px solid {self.COLOR_BORDER};
            }}
            QFrame:hover {{
                border-color: {self.COLOR_BORDER_HOVER};
            }}
        """)
        
        # Drop shadow effect
        shadow = QGraphicsDropShadowEffect(search_wrapper)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        search_wrapper.setGraphicsEffect(shadow)
        
        search_layout = QHBoxLayout(search_wrapper)
        search_layout.setContentsMargins(20, 4, 12, 4)
        search_layout.setSpacing(12)

        # Search input
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search for wallpapers...")
        self.search_edit.setFixedHeight(48)
        self.search_edit.setStyleSheet(f"""
            QLineEdit {{
                font-size: 15px;
                padding: 0px;
                background: transparent;
                border: none;
                color: {self.COLOR_TEXT_PRIMARY};
                selection-background-color: {self.COLOR_ACCENT_PRIMARY};
            }}
            QLineEdit:focus {{
                border: none;
            }}
        """)
        self.search_edit.returnPressed.connect(self.emit_search)
        self.search_edit.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_edit)

        # Clear button
        self.clear_btn = QPushButton("✕")
        self.clear_btn.setFixedSize(28, 28)
        self.clear_btn.setFlat(True)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {self.COLOR_TEXT_MUTED};
                font-size: 14px;
                border: none;
                border-radius: 14px;
            }}
            QPushButton:hover {{
                background: {self.COLOR_BORDER};
                color: {self.COLOR_TEXT_PRIMARY};
            }}
        """)
        self.clear_btn.clicked.connect(self.clear_search)
        self.clear_btn.hide()
        search_layout.addWidget(self.clear_btn)

        container_layout.addWidget(search_wrapper)

        # ============================================================
        # SUBSECTION: Hint & Actions Row
        # ============================================================
        hint_layout = QHBoxLayout()
        hint_layout.setSpacing(10)

        hint = QLabel("⏎ Press Enter to search")
        hint.setAlignment(Qt.AlignLeft)
        hint.setStyleSheet(f"""
            color: {self.COLOR_TEXT_MUTED}; 
            font-size: 12px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
        hint_layout.addWidget(hint)
        hint_layout.addStretch()

        self.explore_label = QLabel(f'or <font color="{self.COLOR_ACCENT_PRIMARY}">explore recent uploads</font> →')
        self.explore_label.setTextFormat(Qt.RichText)
        self.explore_label.setStyleSheet(f"""
            QLabel {{
                color: {self.COLOR_TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 500;
                background: transparent;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
            }}
            QLabel:hover {{
                background-color: {self.COLOR_BG_TERTIARY};
            }}
        """)
        self.explore_label.setCursor(Qt.PointingHandCursor)
        self.explore_label.mousePressEvent = lambda ev: self.emit_explore() if ev.button() == Qt.LeftButton else None
        hint_layout.addWidget(self.explore_label)

        container_layout.addLayout(hint_layout)

        # ============================================================
        # SUBSECTION: Divider
        # ============================================================
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(f"""
            background-color: {self.COLOR_BORDER};
            max-height: 1px;
            border: none;
        """)
        divider.setFixedHeight(1)
        container_layout.addSpacing(8)
        container_layout.addWidget(divider)
        container_layout.addSpacing(8)

        # ============================================================
        # SUBSECTION: Download Location Settings
        # ============================================================
        dir_label = QLabel("DOWNLOAD LOCATION")
        dir_label.setStyleSheet(f"""
            color: {self.COLOR_TEXT_MUTED}; 
            font-size: 11px; 
            font-weight: 700; 
            letter-spacing: 1.5px;
            background: transparent;
            border: none;
        """)
        container_layout.addWidget(dir_label)

        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(8)

        # Path display
        self.dir_edit = QLineEdit()
        self.dir_edit.setText(self.settings.download_folder)
        self.dir_edit.setReadOnly(True)
        self.dir_edit.setFixedHeight(36)
        self.dir_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.COLOR_BG_SECONDARY};
                border: 1px solid {self.COLOR_BORDER};
                border-radius: 6px;
                padding: 0px 12px;
                color: {self.COLOR_TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 500;
            }}
        """)
        dir_layout.addWidget(self.dir_edit)

        # Browse button
        self.browse_btn = QPushButton("Change")
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.setFixedHeight(36)
        self.browse_btn.setCursor(Qt.PointingHandCursor)
        self.browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR_BG_TERTIARY};
                border: 1px solid {self.COLOR_BORDER};
                border-radius: 6px;
                color: {self.COLOR_TEXT_PRIMARY};
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {self.COLOR_BORDER_HOVER};
                border-color: {self.COLOR_ACCENT_PRIMARY};
                color: {self.COLOR_ACCENT_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {self.COLOR_BG_PRIMARY};
            }}
        """)
        self.browse_btn.clicked.connect(self.choose_directory)
        dir_layout.addWidget(self.browse_btn)

        container_layout.addLayout(dir_layout)

        # Add container to main layout
        layout.addWidget(container)
        layout.addStretch()

    # ============================================================
    # SECTION: Event Handlers
    # ============================================================
    def on_search_text_changed(self, text):
        """Toggle clear button visibility."""
        self.clear_btn.setVisible(bool(text))

    def clear_search(self):
        """Clear search field."""
        self.search_edit.clear()
        self.search_edit.setFocus()

    def emit_explore(self):
        """Emit explore signal."""
        self.explore_requested.emit()

    def on_extension_changed(self, name: str):
        """Handle extension changes."""
        if name != "Local":
            self.settings.set_extension(name)

        self.extension_changed.emit(name)

        if name == "Local":
            self.search_edit.setEnabled(False)
            self.search_edit.setPlaceholderText("Browsing local folder...")
            self.search_edit.setStyleSheet(f"""
                QLineEdit {{
                    font-size: 15px;
                    padding: 0px;
                    background: transparent;
                    border: none;
                    color: {self.COLOR_TEXT_MUTED};
                }}
            """)
            self.clear_btn.hide()
            self.status_message.emit("Scanning local folder...")
            self.explore_requested.emit()
        else:
            self.search_edit.setEnabled(True)
            self.search_edit.setPlaceholderText("Search for wallpapers...")
            self.search_edit.setStyleSheet(f"""
                QLineEdit {{
                    font-size: 15px;
                    padding: 0px;
                    background: transparent;
                    border: none;
                    color: {self.COLOR_TEXT_PRIMARY};
                    selection-background-color: {self.COLOR_ACCENT_PRIMARY};
                }}
            """)
            self.on_search_text_changed(self.search_edit.text())
            self.status_message.emit("Ready")

    def emit_search(self):
        """Emit search signal."""
        if not self.search_edit.isEnabled():
            return
        query = self.search_edit.text().strip()
        if query:
            self.search_requested.emit(query)

    def choose_directory(self):
        """Open folder dialog."""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Download Folder", 
            self.settings.download_folder
        )
        if folder:
            self.settings.set_download_folder(folder)
            self.dir_edit.setText(folder)

    def set_search_text(self, text: str):
        """Restore search text."""
        self.search_edit.setText(text)