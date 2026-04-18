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
        self._all_files = []           # Full unfiltered file list
        self._filtered_files = []      # Current filtered view
        self._file_info_cache = {}     # path -> {"size": int, "mtime": float}
        self._last_query = None
        self._last_folder = ""
        self._cache_timestamp = 0
        self._cache_ttl = 300          # 5 minutes

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

    def _get_cached_file_info(self, filepath: str) -> Dict[str, Any]:
        """Get file stats from cache or stat."""
        if filepath in self._file_info_cache:
            return self._file_info_cache[filepath]
        try:
            stat = os.stat(filepath)
            info = {
                "size": stat.st_size,
                "mtime": stat.st_mtime,
            }
            self._file_info_cache[filepath] = info
            return info
        except OSError:
            return {"size": 0, "mtime": 0}

    def search(self, query: str, page: int = 1, **kwargs) -> List[Dict[str, Any]]:
        folder = kwargs.get("download_folder", "./wallpapers")
        sort_by = kwargs.get("sort_by", "modified")

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
            self._last_query = None
            self._file_info_cache.clear()

        # Filter by query
        if query != self._last_query:
            if query and query.strip():
                q = query.lower()
                self._filtered_files = [f for f in self._all_files if q in os.path.basename(f).lower()]
            else:
                self._filtered_files = list(self._all_files)
            self._last_query = query

        # Sort (lightweight, using cached stats)
        if sort_by == "name":
            self._filtered_files.sort(key=lambda f: os.path.basename(f).lower())
        elif sort_by == "size":
            self._filtered_files.sort(
                key=lambda f: self._get_cached_file_info(f)["size"],
                reverse=True
            )
        elif sort_by == "resolution":
            # For resolution sorting we still need dimensions, but we can do it lazily
            # and cache the result to avoid reopening files repeatedly.
            def get_pixel_count(path):
                # Use cached resolution if available
                cache_key = f"res_{path}"
                if hasattr(self, '_res_cache') and cache_key in self._res_cache:
                    return self._res_cache[cache_key]
                try:
                    with Image.open(path) as img:
                        w, h = img.size
                        pixels = w * h
                except Exception:
                    pixels = 0
                if not hasattr(self, '_res_cache'):
                    self._res_cache = {}
                self._res_cache[cache_key] = pixels
                return pixels
            self._filtered_files.sort(key=get_pixel_count, reverse=True)
        else:  # modified
            self._filtered_files.sort(
                key=lambda f: self._get_cached_file_info(f)["mtime"],
                reverse=True
            )

        limit = 24
        start = (page - 1) * limit
        end = start + limit
        page_files = self._filtered_files[start:end]

        # Return basic info without opening every image for resolution
        results = []
        for f in page_files:
            info = self._get_cached_file_info(f)
            results.append({
                "path": f,
                "id": f,
                "resolution": "Loading...",   # Will be updated by widget later
                "file_size": info["size"],
                "modified": info["mtime"],
                "filename": os.path.basename(f),
            })
        return results

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
        # If already loaded by widget, return cached; otherwise "Loading..."
        return wallpaper_data.get("resolution", "Loading...")

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

    def shutdown(self):
        """Clean up any resources."""
        pass