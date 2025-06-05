from django.http import Http404, HttpResponse
from django.shortcuts import render

from module.image_generator.generate_deck_list import generate_card_list_image
from module.scrape.scrape_deck import scrape_deck

DECK_THUMB = "https://www.pokemon-card.com/deck/deckView.php/deckID/{deck_code}.png"


def index(request):
    deck_code = ""
    if request.method == "POST":
        deck_code = request.POST.get("deck_code", "")
    return render(request, "number_of_sheet/index.html", {"deck_code": deck_code})


def question_image(request):
    """
    Returns the question image as a PNG response.
    """
    print("Generating question image")
    deck_code = request.GET.get("deck_code")
    print(f"Deck code: {deck_code}")
    if not deck_code:
        return Http404("Deck code is required")

    try:
        deck = scrape_deck(deck_code)
        print(f"Deck scraped: {deck.name} ({deck.code})")
        question_image = generate_card_list_image(deck.cards, with_image=False)
        response = HttpResponse(content_type="image/png")
        question_image.save(response, format="PNG")
        return response
    except ValueError as e:
        print(e)
        return HttpResponse(str(e), status=400)
