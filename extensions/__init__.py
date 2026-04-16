from .wallhaven import WallhavenExtension
from .danbooru import DanbooruExtension
from core.extension import register_extension

register_extension("Wallhaven", WallhavenExtension)
register_extension("Danbooru", DanbooruExtension)