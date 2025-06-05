import requests
from bs4 import BeautifulSoup

from ..domain.value_objects import Card, CardType, Deck

BASE_URL = "https://www.pokemon-card.com"
DECK_URL = BASE_URL + "/deck/confirm.html/deckID/{deck_code}"


def fetch_soup(url: str) -> BeautifulSoup:
    html = requests.get(url).text
    return BeautifulSoup(html, "html.parser")


def scrape_deck(code: str) -> Deck:
    soup = fetch_soup(DECK_URL.format(deck_code=code))
    card_info = max(soup.find_all("script"), key=lambda s: len(s.text)).text

    cards = []
    pokemons_line = soup.find("input", {"name": "deck_pke"}).get("value")
    cards += [
        _create_card(card_id, CardType.POKEMON, count, card_info)
        for (card_id, count) in _format_card_line(pokemons_line)
    ]
    goods_line = soup.find("input", {"name": "deck_gds"}).get("value")
    cards += [
        _create_card(card_id, CardType.GOODS, count, card_info)
        for (card_id, count) in _format_card_line(goods_line)
    ]
    tools_line = soup.find("input", {"name": "deck_tool"}).get("value")
    cards += [
        _create_card(card_id, CardType.TOOL, count, card_info)
        for (card_id, count) in _format_card_line(tools_line)
    ]
    supporters_line = soup.find("input", {"name": "deck_sup"}).get("value")
    cards += [
        _create_card(card_id, CardType.SUPPORTER, count, card_info)
        for (card_id, count) in _format_card_line(supporters_line)
    ]
    statiums_line = soup.find("input", {"name": "deck_sta"}).get("value")
    cards += [
        _create_card(card_id, CardType.STADIUM, count, card_info)
        for (card_id, count) in _format_card_line(statiums_line)
    ]
    energies_line = soup.find("input", {"name": "deck_ene"}).get("value")
    cards += [
        _create_card(card_id, CardType.ENERGY, count, card_info)
        for (card_id, count) in _format_card_line(energies_line)
    ]
    # techs = soup.find("input", {"name": "deck_tech"}).get("value")  # 恐らく昔の技マシン
    # ajs = soup.find("input", {"name": "deck_ajs"}).get("value")  # 恐らく調整用カード

    deck = Deck(code, cards)
    if not deck.validate():
        raise ValueError("Invalid deck")

    return deck


def _format_card_line(card_line: str) -> list[tuple[str, int]]:
    """
    Args:
        card_line (str): card line in the format of "{card_id}_{count}_{unknown}-..."
    Returns:
        list[tuple[int, int]]: list of tuples of card_id and count
    """
    cards = []
    for c in card_line.split("-"):
        if not c:
            continue
        card_id, count, _ = c.split("_")  # 3つ目の要素は不明だが、今のところ使わない
        cards.append((card_id, int(count)))
    return cards


def _create_card(card_id: str, card_type: CardType, card_count: int, card_info: str) -> Card:
    name = search_value(card_info, f"PCGDECK.searchItemNameAlt[{card_id}]")
    img_url = BASE_URL + search_value(card_info, f"PCGDECK.searchItemCardPict[{card_id}]")
    return Card(name, card_type, card_id, img_url, card_count)


def search_value(source: str, target: str) -> str:
    for line in source.split("\n"):
        if target in line:
            value = line
            value = value.replace(target, "")
            value = value.replace("=", "")
            value = value.replace(";", "")
            value = value.replace("'", "")
            value = value.replace("\r", "")
            return value
