import traceback

from django.conf import settings
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
    deck_code = request.GET.get("deck_code")
    if not deck_code:
        return Http404("Deck code is required")

    try:
        deck = scrape_deck(deck_code)
        question_image = generate_card_list_image(deck.cards, False, settings.TIMES_BOLD_FONT_PATH)
        response = HttpResponse(content_type="image/png")
        question_image.save(response, format="PNG")
        return response
    except Exception as e:
        traceback.print_exc()
        return HttpResponse(str(e), status=400)
