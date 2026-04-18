import os
import math
import time
from typing import List, Dict, Any
from PIL import Image
from core.extension import WallpaperExtension


class LocalExtension(WallpaperExtension):
    """Browse downloaded wallpapers from local folder with caching."""

    def __init__(self):
        super().__init__()
        self.name = "Local"
        self._all_files = []       # Full unfiltered file list
        self._filtered_files = []  # Current filtered view
        self._last_query = None
        self._last_folder = ""
        self._cache_timestamp = 0
        self._cache_ttl = 300      # 5 minutes

    def _get_image_files(self, folder: str) -> List[str]:
        """Recursively find all image files in folder."""
        extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        files = []
        try:
            for root, _, filenames in os.walk(folder):
                for f in filenames:
                    if f.lower().endswith(extensions):
                        files.append(os.path.join(root, f))
        except Exception:
            pass
        return files

    def _get_image_info(self, filepath: str) -> Dict[str, Any]:
        """Extract metadata from an image file."""
        try:
            with Image.open(filepath) as img:
                width, height = img.size
        except Exception:
            width, height = 0, 0

        stat = os.stat(filepath)
        return {
            "path": filepath,
            "id": filepath,
            "resolution": f"{width}x{height}" if width else "?x?",
            "file_size": stat.st_size,
            "modified": stat.st_mtime,
            "filename": os.path.basename(filepath),
        }

    def search(self, query: str, page: int = 1, **kwargs) -> List[Dict[str, Any]]:
        folder = kwargs.get("download_folder", "./wallpapers")
        sort_by = kwargs.get("sort_by", "modified")  # name, modified, size, resolution

        now = time.time()
        cache_valid = (
            folder == self._last_folder and 
            now - self._cache_timestamp < self._cache_ttl and
            self._all_files
        )

        if not cache_valid:
            self._all_files = self._get_image_files(folder)
            self._last_folder = folder
            self._cache_timestamp = now
            self._last_query = None  # Force re-filter

        # Apply filtering if query changed
        if query != self._last_query:
            if query and query.strip():
                q = query.lower()
                self._filtered_files = [f for f in self._all_files if q in os.path.basename(f).lower()]
            else:
                self._filtered_files = list(self._all_files)
            self._last_query = query

        # Apply sorting (lightweight: in-memory, no extra I/O)
        if sort_by == "name":
            self._filtered_files.sort(key=lambda f: os.path.basename(f).lower())
        elif sort_by == "size":
            self._filtered_files.sort(key=lambda f: os.stat(f).st_size, reverse=True)
        elif sort_by == "resolution":
            # Sort by pixel count (width * height)
            def get_pixels(path):
                try:
                    with Image.open(path) as img:
                        w, h = img.size
                        return w * h
                except:
                    return 0
            self._filtered_files.sort(key=get_pixels, reverse=True)
        else:  # modified (default)
            self._filtered_files.sort(key=lambda f: os.stat(f).st_mtime, reverse=True)

        limit = 24
        start = (page - 1) * limit
        end = start + limit
        page_files = self._filtered_files[start:end]

        return [self._get_image_info(f) for f in page_files]

    def get_total_pages(self, query: str, **kwargs) -> int:
        limit = 24
        return math.ceil(len(self._filtered_files) / limit) if self._filtered_files else 1

    def get_thumbnail_url(self, wallpaper_data: Dict[str, Any]) -> str:
        return wallpaper_data.get("path", "")

    def get_download_url(self, wallpaper_data: Dict[str, Any]) -> str:
        return wallpaper_data.get("path", "")

    def get_wallpaper_id(self, wallpaper_data: Dict[str, Any]) -> str:
        return wallpaper_data.get("id", "")

    def get_file_extension(self, wallpaper_data: Dict[str, Any]) -> str:
        path = wallpaper_data.get("path", "")
        ext = os.path.splitext(path)[1].lstrip('.').lower()
        return ext if ext else "jpg"

    def get_resolution(self, wallpaper_data: Dict[str, Any]) -> str:
        return wallpaper_data.get("resolution", "?x?")

    def get_filters(self) -> Dict[str, Any]:
        return {
            "sort_by": {
                "type": "dropdown",
                "label": "Sort by",
                "options": [
                    {"id": "modified", "label": "Date Modified", "default": True},
                    {"id": "name", "label": "Name (A-Z)", "default": False},
                    {"id": "size", "label": "File Size", "default": False},
                    {"id": "resolution", "label": "Resolution", "default": False},
                ]
            }
        }