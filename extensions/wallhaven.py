import requests
from typing import List, Dict, Any
from core.extension import WallpaperExtension


class WallhavenExtension(WallpaperExtension):
    """Wallhaven.cc API implementation."""
    
    def __init__(self):
        super().__init__()
        self.name = "Wallhaven"
        self.api_url = "https://wallhaven.cc/api/v1/search"
        self._last_meta = {}
    
    def search(self, query: str, page: int = 1, **kwargs) -> List[Dict[str, Any]]:
        category = kwargs.get("category", "111")
        purity = kwargs.get("purity", "100")
        
        params = {
            "q": query,
            "categories": category,
            "purity": purity,
            "page": page,
            "sorting": "date_added",
            "order": "desc"
        }
        response = requests.get(self.api_url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        self._last_meta = data.get("meta", {})
        return data.get("data", [])
    
    def get_total_pages(self, query: str, **kwargs) -> int:
        return self._last_meta.get("last_page", 1)
    
    def get_thumbnail_url(self, wallpaper_data: Dict[str, Any]) -> str:
        return wallpaper_data.get("thumbs", {}).get("large", "")
    
    def get_download_url(self, wallpaper_data: Dict[str, Any]) -> str:
        return wallpaper_data.get("path", "")
    
    def get_wallpaper_id(self, wallpaper_data: Dict[str, Any]) -> str:
        return wallpaper_data.get("id", "")
    
    def get_file_extension(self, wallpaper_data: Dict[str, Any]) -> str:
        file_type = wallpaper_data.get("file_type", "image/jpeg")
        if "jpeg" in file_type or "jpg" in file_type:
            return "jpg"
        elif "png" in file_type:
            return "png"
        return "jpg"
    
    def get_resolution(self, wallpaper_data: Dict[str, Any]) -> str:
        return wallpaper_data.get("resolution", "?x?")