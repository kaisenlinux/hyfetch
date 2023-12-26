from __future__ import annotations

from dataclasses import dataclass, field

from .constants import CONFIG_PATH
from .neofetch_util import ColorAlignment
from .serializer import json_stringify, from_dict
from .types import AnsiMode, LightDark, BackendLiteral


@dataclass
class Config:
    preset: str
    mode: AnsiMode
    light_dark: LightDark = 'dark'
    lightness: float | None = None
    color_align: ColorAlignment = field(default_factory=lambda: ColorAlignment('horizontal'))
    backend: BackendLiteral = "neofetch"
    args: str | None = None
    distro: str | None = None
    pride_month_shown: list[int] = field(default_factory=list)  # This is deprecated, see issue #136
    pride_month_disable: bool = False

    @classmethod
    def from_dict(cls, d: dict):
        d['color_align'] = ColorAlignment.from_dict(d['color_align'])
        return from_dict(cls, d)

    def save(self):
        CONFIG_PATH.parent.mkdir(exist_ok=True, parents=True)
        CONFIG_PATH.write_text(json_stringify(self, indent=4), 'utf-8')
