from .wallhaven import WallhavenExtension
# from .danbooru import DanbooruExtension
from .local import LocalExtension
from .fourkwallpapers import FourKWallpapersExtension
from core.extension import register_extension

register_extension("4kwallpapers(TEST)", FourKWallpapersExtension)
register_extension("Wallhaven", WallhavenExtension)
# Off-ing Danbooru for now since it has a lot of NSFW content and is less relevant to the main use case
# register_extension("Danbooru", DanbooruExtension)
register_extension("Local", LocalExtension)
