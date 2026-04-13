from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from PyQt5.QtCore import QObject


class WallpaperExtension(ABC):
    """Abstract base class for wallpaper sources."""
    
    def __init__(self):
        self.name = "Base Extension"
    
    @abstractmethod
    def search(self, query: str, page: int = 1, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for wallpapers.
        
        Returns:
            List of wallpaper data dicts.
        """
        pass
    
    @abstractmethod
    def get_total_pages(self, query: str, **kwargs) -> int:
        """Return total number of pages for a query."""
        pass
    
    @abstractmethod
    def get_thumbnail_url(self, wallpaper_data: Dict[str, Any]) -> str:
        """Extract thumbnail URL from wallpaper data."""
        pass
    
    @abstractmethod
    def get_download_url(self, wallpaper_data: Dict[str, Any]) -> str:
        """Extract full image URL from wallpaper data."""
        pass
    
    @abstractmethod
    def get_wallpaper_id(self, wallpaper_data: Dict[str, Any]) -> str:
        """Return unique identifier for the wallpaper."""
        pass
    
    @abstractmethod
    def get_file_extension(self, wallpaper_data: Dict[str, Any]) -> str:
        """Return file extension (e.g., 'jpg', 'png')."""
        pass
    
    @abstractmethod
    def get_resolution(self, wallpaper_data: Dict[str, Any]) -> str:
        """Return resolution string (e.g., '1920x1080')."""
        pass