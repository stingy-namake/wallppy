import json
import os
from pathlib import Path
from typing import Dict, Any


DEFAULT_DOWNLOAD_FOLDER = "./wallpapers"
DEFAULT_CATEGORIES = {"general": True, "anime": True, "people": True}
DEFAULT_PURITY = {"sfw": True, "sketchy": False}


class Settings:
    """Persistent application settings."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "wallppy"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.config_dir / "settings.json"
        
        self.download_folder = DEFAULT_DOWNLOAD_FOLDER
        self.categories = DEFAULT_CATEGORIES.copy()
        self.purity = DEFAULT_PURITY.copy()
        self.load()
        os.makedirs(self.download_folder, exist_ok=True)
    
    def load(self):
        """Load settings from config file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.download_folder = data.get("download_folder", DEFAULT_DOWNLOAD_FOLDER)
                    self.categories = data.get("categories", DEFAULT_CATEGORIES)
                    self.purity = data.get("purity", DEFAULT_PURITY)
            except Exception:
                pass
    
    def save(self):
        """Save settings to config file."""
        data = {
            "download_folder": self.download_folder,
            "categories": self.categories,
            "purity": self.purity
        }
        try:
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    def set_download_folder(self, folder: str):
        self.download_folder = folder
        os.makedirs(folder, exist_ok=True)
        self.save()
    
    def set_categories(self, general: bool, anime: bool, people: bool):
        self.categories = {"general": general, "anime": anime, "people": people}
        self.save()
    
    def set_purity(self, sfw: bool, sketchy: bool):
        self.purity = {"sfw": sfw, "sketchy": sketchy}
        self.save()