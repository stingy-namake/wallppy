import os
import math
from typing import List, Dict, Any
from PIL import Image
from core.extension import WallpaperExtension


class LocalExtension(WallpaperExtension):
    """Browse downloaded wallpapers from local folder."""

    def __init__(self):
        super().__init__()
        self.name = "Local"
        self._last_files = []
        self._last_query = None          # Use None to distinguish from empty string
        self._last_folder = ""

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
        self._base_folder = folder

        # Reset cache if folder changed
        if folder != self._last_folder:
            self._last_files = []
            self._last_query = None
            self._last_folder = folder

        # Rebuild file list if query changed (including None -> "" transition)
        if query != self._last_query or not self._last_files:
            all_files = self._get_image_files(folder)
            # Filter by query if non-empty
            if query.strip():
                q = query.lower()
                all_files = [f for f in all_files if q in os.path.basename(f).lower()]
            self._last_files = all_files
            self._last_query = query

        limit = 24
        start = (page - 1) * limit
        end = start + limit
        page_files = self._last_files[start:end]

        return [self._get_image_info(f) for f in page_files]

    def get_total_pages(self, query: str, **kwargs) -> int:
        limit = 24
        return math.ceil(len(self._last_files) / limit) if self._last_files else 1

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
        return {}