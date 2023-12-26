from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from pathlib import Path

from .types import LightDark
from .__version__ import VERSION

CONFIG_PATH = Path.home() / '.config/hyfetch.json'


TEST_ASCII = r"""
### |\___/| ###
### )     ( ###
## =\     /= ##
#### )===( ####
### /     \ ###
### |     | ###
## / {txt} \ ##
## \       / ##
_/\_\_   _/_/\_
|##|  ( (  |##|
|##|   ) ) |##|
|##|  (_(  |##|""".strip('\n')

TEST_ASCII_WIDTH = max(len(line) for line in TEST_ASCII.split('\n'))
DEFAULT_DARK_L = 0.
IS_WINDOWS = platform.system() == 'Windows'

CACHE_PATH = Path(os.getenv("LOCALAPPDATA") or os.getenv("XDG_CACHE_HOME") or Path.home() / '.cache') / 'hyfetch'

@dataclass
class GlobalConfig:
    # Global color mode default to 8-bit for compatibility
    color_mode: str
    override_distro: str | None
    debug: bool
    is_light: bool
    use_overlay: bool

    def light_dark(self) -> LightDark:
        return 'light' if self.is_light else 'dark'

    def default_lightness(self, term: LightDark | None = None) -> float:
        if term is None:
            term = self.light_dark()
        return 0.65 if term.lower() == 'dark' else 0.4


GLOBAL_CFG = GlobalConfig(color_mode='8bit', override_distro=None, debug=False, is_light=False, use_overlay=False)

MINGIT_URL = 'https://github.com/git-for-windows/git/releases/download/v2.37.2.windows.2/MinGit-2.37.2.2-busybox-32-bit.zip'
