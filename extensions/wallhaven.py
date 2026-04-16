import requests
from typing import List, Dict, Any
from core.extension import WallpaperExtension


class WallhavenExtension(WallpaperExtension):
    """Wallhaven.cc API implementation."""
    
    def __init__(self, api_key: str = None):
        super().__init__()
        self.name = "Wallhaven"
        self.api_url = "https://wallhaven.cc/api/v1/search"
        self.api_key = api_key
        self._last_meta = {}
    
    def _get_headers(self) -> Dict[str, str]:
        """Return headers required by Wallhaven API."""
        headers = {
            "User-Agent": "wallppy/1.0 (https://github.com/yourrepo; your-email@example.com)"
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
    
    def search(self, query: str, page: int = 1, **kwargs) -> List[Dict[str, Any]]:
        category = str(kwargs.get("category", "111")).strip()
        purity = str(kwargs.get("purity", "100")).strip()
        
        params = {
            "q": query,
            "categories": category,
            "purity": purity,
            "page": page,
            "sorting": "date_added",
            "order": "desc"
        }
        try:
            response = requests.get(
                self.api_url,
                params=params,
                headers=self._get_headers(),
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            self._last_meta = data.get("meta", {})
            return data.get("data", [])
        except Exception as e:
            print(f"Wallhaven error: {e}")
            return []
    
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
    
    def get_filters(self) -> Dict[str, Any]:
        return {
            "categories": {
                "type": "checkboxes",
                "label": "Categories",
                "options": [
                    {"id": "general", "label": "General", "default": False},
                    {"id": "anime", "label": "Anime", "default": True},
                    {"id": "people", "label": "People", "default": False}
                ]
            },
            "purity": {
                "type": "checkboxes",
                "label": "Content",
                "options": [
                    {"id": "sfw", "label": "SFW", "default": True},
                    {"id": "sketchy", "label": "Sketchy", "default": False},
                    {"id": "nsfw", "label": "NSFW", "default": False, "requires_api_key": True}
                ]
            }
        }