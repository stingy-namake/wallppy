from .wallhaven import WallhavenExtension
from .danbooru import DanbooruExtension
from .local import LocalExtension
from core.extension import register_extension

register_extension("Wallhaven", WallhavenExtension)
register_extension("Danbooru", DanbooruExtension)
register_extension("Local", LocalExtension)