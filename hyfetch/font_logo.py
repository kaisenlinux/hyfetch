import json
from pathlib import Path

from hyfetch.constants import CACHE_PATH
from hyfetch.neofetch_util import get_distro_name


def get_font_logo() -> str:
    cache = CACHE_PATH / 'font_logo_cache.txt'
    if cache.exists():
        return cache.read_text('utf-8')

    font_logos: dict[str, str] = json.loads((Path(__file__).parent / 'data/font_logos.json').read_text('utf-8'))
    font_logos = {k.lower(): v for k, v in font_logos.items()}

    # Get the distro
    distro = get_distro_name().lower()

    # Find most likely distro by containing string
    for k in font_logos.keys():
        if k in distro:
            distro = k
    # If not found, try matching partial string (by splitting with " ")
    if not distro:
        for k in font_logos.keys():
            if any(x in distro for x in k.split(' ')):
                distro = k
    # If still not found, give up
    if not distro:
        raise ValueError(f'No font logo found for distro: {distro}. The supported logos are in https://github.com/Lukas-W/font-logos')

    logo = font_logos[distro]
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(logo)

    return logo

