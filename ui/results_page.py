import random
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QScrollArea, QGridLayout, QFrame, QStackedWidget,
    QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from core.extension import WallpaperExtension
from core.settings import Settings
from core.workers import SearchWorker, DownloadWorker
from .wallpaper_widget import WallpaperWidget


THUMB_SIZE = QSize(280, 158)
THUMB_PADDING = 12

NO_RESULTS_MESSAGES = [
    "Nothing here... Maybe it's in another world?",
    "This search result is a lie.",
    "No wallpapers found. Believe it!",
    "The data is empty. Just like my soul.",
    "404: Wallpapers Not Found. Try a different keyword, nya~",
    "Even the Great Sage couldn't find anything.",
    "This search returned void. Like the Abyss.",
    "No results. Perhaps you need the Sharingan to see them?",
]


class ResultsPage(QWidget):
    home_requested = pyqtSignal()
    search_requested = pyqtSignal(str)
    download_progress = pyqtSignal(int)
    download_finished = pyqtSignal(bool, str, str, str)
    
    def __init__(self, extension: WallpaperExtension, settings: Settings, parent=None):
        super().__init__(parent)
        self.extension = extension
        self.settings = settings
        self.current_query = ""
        self.current_page = 1
        self.total_pages = 1
        self.wallpapers = []
        self.columns = 3
        self.is_loading = False
        self.workers = []
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Top bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)
        
        self.home_btn = QPushButton("⌂")
        self.home_btn.setToolTip("Back to home")
        self.home_btn.setFixedSize(36, 36)
        self.home_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #3d3d3d;
                border-radius: 18px;
                font-size: 20px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
        """)
        self.home_btn.clicked.connect(self.home_requested.emit)
        top_bar.addWidget(self.home_btn)
        
        search_layout = QHBoxLayout()
        search_layout.setSpacing(0)
        search_icon = QLabel()
        search_icon.setPixmap(QIcon.fromTheme("system-search").pixmap(16,16))
        search_layout.addWidget(search_icon)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search wallpapers...")
        self.search_edit.returnPressed.connect(self.emit_search)
        search_layout.addWidget(self.search_edit)
        top_bar.addLayout(search_layout, 3)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.emit_search)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E6FF0;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #3D82F5;
            }
            QPushButton:pressed {
                background-color: #1558C4;
            }
        """)
        top_bar.addWidget(self.search_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)
        
        # Results container (grid + no-results)
        self.results_container = QStackedWidget()
        layout.addWidget(self.results_container)
        
        # Grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.setSpacing(THUMB_PADDING)
        self.grid_layout.setContentsMargins(4, 4, 4, 4)
        
        self.scroll_area.setWidget(self.grid_widget)
        self.results_container.addWidget(self.scroll_area)
        
        # No results
        self.no_results_widget = QWidget()
        no_results_layout = QVBoxLayout(self.no_results_widget)
        no_results_layout.setAlignment(Qt.AlignCenter)
        self.no_results_label = QLabel()
        self.no_results_label.setAlignment(Qt.AlignCenter)
        self.no_results_label.setStyleSheet("color: #aaa; font-size: 18px; padding: 40px;")
        self.no_results_label.setWordWrap(True)
        no_results_layout.addWidget(self.no_results_label)
        self.results_container.addWidget(self.no_results_widget)
        
        # Loading indicator
        self.loading_progress = QProgressBar()
        self.loading_progress.setVisible(False)
        self.loading_progress.setRange(0, 0)
        layout.addWidget(self.loading_progress)
        
        self.scroll_area.viewport().installEventFilter(self)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)
    
    def eventFilter(self, obj, event):
        if obj == self.scroll_area.viewport() and event.type() == event.Resize:
            if self.update_columns_from_width() and self.wallpapers:
                self.rebuild_grid()
        return super().eventFilter(obj, event)
    
    def update_columns_from_width(self):
        viewport_width = self.scroll_area.viewport().width()
        thumb_width_total = THUMB_SIZE.width() + 20 + THUMB_PADDING
        if thumb_width_total > 0:
            new_cols = max(1, viewport_width // thumb_width_total)
            if new_cols != self.columns:
                self.columns = new_cols
                return True
        return False
    
    def on_scroll(self, value):
        if self.is_loading or self.current_page >= self.total_pages:
            return
        scrollbar = self.scroll_area.verticalScrollBar()
        if scrollbar.maximum() - value < 200:
            self.load_next_page()
    
    def emit_search(self):
        query = self.search_edit.text().strip()
        if query:
            self.search_requested.emit(query)
    
    def start_search(self, query: str, category: str, purity: str):
        self.current_query = query
        self.search_edit.setText(query)
        self.current_page = 1
        self.wallpapers = []
        self.total_pages = 1
        self.is_loading = True
        self.loading_progress.setVisible(True)
        self.results_container.setCurrentIndex(0)
        
        self.worker = SearchWorker(
            self.extension,
            query,
            self.current_page,
            category=category,
            purity=purity
        )
        self.worker.finished.connect(self.on_search_finished)
        self.worker.error.connect(self.on_search_error)
        self.worker.start()
        self.workers.append(self.worker)
    
    def load_next_page(self):
        if self.is_loading or self.current_page >= self.total_pages:
            return
        
        self.is_loading = True
        self.loading_progress.setVisible(True)
        
        # Get category/purity from main window via parent
        main_win = self.window()
        category = main_win.landing_page.get_category_string()
        purity = main_win.landing_page.get_purity_string()
        
        self.worker = SearchWorker(
            self.extension,
            self.current_query,
            self.current_page + 1,
            category=category,
            purity=purity
        )
        self.worker.finished.connect(self.on_search_finished)
        self.worker.error.connect(self.on_search_error)
        self.worker.start()
        self.workers.append(self.worker)
    
    def on_search_finished(self, wallpapers, page, total_pages):
        self.is_loading = False
        self.loading_progress.setVisible(False)
        
        if page == 1:
            self.wallpapers = wallpapers
            self.total_pages = total_pages
            self.current_page = 1
            if not wallpapers:
                self.show_no_results()
            else:
                self.results_container.setCurrentIndex(0)
                self.rebuild_grid()
        else:
            self.wallpapers.extend(wallpapers)
            self.current_page = page
            self.total_pages = total_pages
            self.append_to_grid(wallpapers)
    
    def on_search_error(self, error_msg):
        self.is_loading = False
        self.loading_progress.setVisible(False)
        QMessageBox.critical(self, "Search Error", error_msg)
    
    def show_no_results(self):
        message = random.choice(NO_RESULTS_MESSAGES)
        self.no_results_label.setText(message)
        self.results_container.setCurrentIndex(1)
    
    def rebuild_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.wallpapers:
            return
        
        self.update_columns_from_width()
        
        for i, wp in enumerate(self.wallpapers):
            row = i // self.columns
            col = i % self.columns
            widget = WallpaperWidget(self.extension, wp, self.settings.download_folder)
            widget.download_triggered.connect(self.download_wallpaper)
            self.grid_layout.addWidget(widget, row, col)
        
        row_count = (len(self.wallpapers) - 1) // self.columns + 1
        self.grid_layout.setRowStretch(row_count, 1)
    
    def append_to_grid(self, new_wallpapers):
        start_index = len(self.wallpapers) - len(new_wallpapers)
        for i, wp in enumerate(new_wallpapers):
            global_index = start_index + i
            row = global_index // self.columns
            col = global_index % self.columns
            widget = WallpaperWidget(self.extension, wp, self.settings.download_folder)
            widget.download_triggered.connect(self.download_wallpaper)
            self.grid_layout.addWidget(widget, row, col)
        
        row_count = (len(self.wallpapers) - 1) // self.columns + 1
        self.grid_layout.setRowStretch(row_count, 1)
    
    def download_wallpaper(self, wallpaper_data):
        self.download_progress.emit(0)
        self.dl_worker = DownloadWorker(self.extension, wallpaper_data, self.settings.download_folder)
        self.dl_worker.finished.connect(self.on_download_finished)
        self.dl_worker.progress.connect(self.download_progress.emit)
        self.dl_worker.start()
        self.workers.append(self.dl_worker)
    
    def on_download_finished(self, success, filepath, filename, wall_id):
        self.download_finished.emit(success, filepath, filename, wall_id)
        if success:
            # Update checkmark on matching widget
            for i in range(self.grid_layout.count()):
                widget = self.grid_layout.itemAt(i).widget()
                if isinstance(widget, WallpaperWidget):
                    if self.extension.get_wallpaper_id(widget.data) == wall_id:
                        widget.update_downloaded_status()
                        break
    
    def update_download_folder(self):
        """Update all widgets with new download folder."""
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, WallpaperWidget):
                widget.download_folder = self.settings.download_folder
                widget.update_downloaded_status()