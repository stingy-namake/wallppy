import sys
import os
import requests
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from typing import List, Dict, Any
from .extension import WallpaperExtension


class SearchWorker(QThread):
    finished = pyqtSignal(list, int, int)  # wallpapers, page, total_pages
    error = pyqtSignal(str)
    
    def __init__(self, extension: WallpaperExtension, query: str, page: int = 1, **kwargs):
        super().__init__()
        self.extension = extension
        self.query = query
        self.page = page
        self.kwargs = kwargs
    
    def run(self):
        try:
            wallpapers = self.extension.search(self.query, self.page, **self.kwargs)
            total_pages = self.extension.get_total_pages(self.query, **self.kwargs)
            self.finished.emit(wallpapers, self.page, total_pages)
        except Exception as e:
            self.error.emit(str(e))


class DownloadWorker(QThread):
    finished = pyqtSignal(bool, str, str, str)  # success, filepath, filename, wall_id
    progress = pyqtSignal(int)
    
    def __init__(self, extension: WallpaperExtension, wallpaper_data: Dict[str, Any], download_folder: str):
        super().__init__()
        self.extension = extension
        self.data = wallpaper_data
        self.download_folder = download_folder
    
    def run(self):
        download_url = self.extension.get_download_url(self.data)
        wall_id = self.extension.get_wallpaper_id(self.data)
        if not download_url:
            self.finished.emit(False, "", "No image URL", wall_id)
            return
        
        ext = self.extension.get_file_extension(self.data)
        filename = f"wallppy-{wall_id}.{ext}"
        filepath = os.path.join(self.download_folder, filename)
        
        if os.path.exists(filepath):
            self.finished.emit(True, filepath, filename, wall_id)
            return
        
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            self.progress.emit(int(downloaded * 100 / total_size))
            self.finished.emit(True, filepath, filename, wall_id)
        except Exception as e:
            self.finished.emit(False, "", str(e), wall_id)


class ThumbnailLoader(QThread):
    loaded = pyqtSignal(QPixmap)
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.loaded.emit(pixmap)
            else:
                self.loaded.emit(QPixmap())
        except:
            self.loaded.emit(QPixmap())