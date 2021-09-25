from dataclasses import dataclass
from enum import Enum


class System(Enum):
    MAC = 0
    WINDOWS = 1
    BOT = 2


@dataclass
class KeyboardShortcut:
    category: str
    command: str
    description: str
    category_description: str = ''


@dataclass
class Parameter:
    key: str
    value: str
