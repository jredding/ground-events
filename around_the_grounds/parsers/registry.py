from typing import Dict, Type

from .bale_breaker import BaleBreakerParser
from .base import BaseParser
from .chucks_greenwood import ChucksGreenwoodParser
from .littlefield import LittlefieldParser
from .obec_brewing import ObecBrewingParser
from .roulette import RouletteParser
from .salehs_corner import SalehsCornerParser
from .stoup_ballard import StoupBallardParser
from .union_hall import UnionHallParser
from .urban_family import UrbanFamilyParser
from .wheelie_pop import WheeliePopParser


class ParserRegistry:
    _parsers: Dict[str, Type[BaseParser]] = {
        "stoup-ballard": StoupBallardParser,
        "yonder-balebreaker": BaleBreakerParser,
        "obec-brewing": ObecBrewingParser,
        "urban-family": UrbanFamilyParser,
        "wheelie-pop": WheeliePopParser,
        "chucks-greenwood": ChucksGreenwoodParser,
        "salehs-corner": SalehsCornerParser,
        "roulette": RouletteParser,
        "littlefield": LittlefieldParser,
        "union-hall": UnionHallParser,
    }

    @classmethod
    def get_parser(cls, key: str) -> Type[BaseParser]:
        if key not in cls._parsers:
            raise ValueError(f"No parser found for key: {key}")
        return cls._parsers[key]

    @classmethod
    def register_parser(cls, key: str, parser_class: Type[BaseParser]) -> None:
        cls._parsers[key] = parser_class

    @classmethod
    def get_supported_keys(cls) -> list:
        return list(cls._parsers.keys())
