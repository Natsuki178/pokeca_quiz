from dataclasses import dataclass, field
from enum import Enum


class CardType(Enum):
    POKEMON = "ポケモン"
    GOODS = "グッズ"
    TOOL = "持ち物"
    SUPPORTER = "サポート"
    STADIUM = "スタジアム"
    ENERGY = "エネルギー"


@dataclass
class Card:
    name: str
    type: CardType
    id: str
    img_url: str
    count: int | None

    def is_same_card(self, other: object) -> bool:
        return self.name == other.name

    @property
    def expantion(self) -> str:
        return self.img_url.split("/")[-2]

    def to_list(self) -> list:
        return [self.name, self.type.name, self.id, self.img_url, self.count, self.expantion]


@dataclass
class Deck:
    code: str
    cards: list[Card] = field(default_factory=list)

    def validate(cls) -> bool:
        # deck must have 60 cards
        count = sum([card.count for card in cls.cards if card.count is not None])
        return count == 60

    def kind_count(self) -> int:
        return len(self.cards)
