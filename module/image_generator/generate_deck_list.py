import requests
from PIL import Image, ImageDraw, ImageFont

from ..domain.value_objects import Card

CARD_WIDHTH = 420
CARD_HEIGHT = 560
COLMUN_COUNT = 5


def nearrest_multiple(value: int, multiple: int, minimum: int) -> int:
    i = minimum
    while True:
        if value <= multiple * i:
            return i
        i += 1


def calc_row_colmun(kind: int) -> tuple[int, int]:
    if kind <= 6:
        return 1, kind
    elif kind <= 16:
        return 2, nearrest_multiple(kind, 2, 6)
    elif kind <= 27:
        return 3, nearrest_multiple(kind, 3, 8)
    else:
        return 4, nearrest_multiple(kind, 4, 9)


def draw_count(draw: ImageDraw.Draw, count: int) -> None:
    """
    Draw the count on the image.

    Args:
        draw (ImageDraw.Draw): ImageDraw object to draw on.
        count (int): Count to be drawn.
    """
    # Define font size and position
    imw, imh = draw.im.size
    count_width = int(imw / 4)
    count_height = font_size = int(imh / 8)
    font = ImageFont.truetype("times.ttf", font_size)  # Load a font

    count_center = (imw // 2, imh - count_height // 2)
    draw.rectangle(
        (
            count_center[0] - count_width // 2,
            count_center[1] - count_height // 2,
            count_center[0] + count_width // 2,
            count_center[1] + count_height // 2,
        ),
        fill=(0, 0, 0),  # Semi-transparent black background
    )
    draw.text(
        count_center,
        str(count),
        fill=(255, 255, 255),  # White text
        font=font,
        anchor="mm",
    )


def download_image(url: str) -> Image.Image:
    """
    Download an image from a URL and convert it to a NumPy array.

    Args:
        url (str): URL of the image.

    Returns:
        Image.Image: Downloaded image as a PIL Image.
    """
    response = requests.get(url)
    ext = url.split(".")[-1].lower()
    if response.status_code != 200:
        raise Exception(f"Failed to download image from {url}")
    with open(f"temp.{ext}", "wb") as f:
        f.write(response.content)
    image = Image.open(f"temp.{ext}")
    if image.mode != "RGB":
        image = image.convert("RGB")

    if image.size[0] > image.size[1]:
        image = image.transpose(Image.ROTATE_90)
    return image


def generate_card_image(card: Card, width: int, height: int, with_image: bool) -> Image.Image:
    """
    Generate a card image with the specified count, width, and height.

    Args:
        card (Card | None): Card object containing the URL and count.
        width (int): Width of the card image.
        height (int): Height of the card image.

    Returns:
        Image.Image: Generated card image with the specified count.
    """
    if card is None:
        return Image.new("RGB", (width, height), (255, 255, 255))  # Transparent image
    # Read the card image from the URL
    if with_image:
        card_image = download_image(card.url)
        card_image = card_image.resize((width, height), Image.Resampling.LANCZOS)

    card_image = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(card_image)
    draw_count(draw, card.count)

    return card_image


def image_concat_vertically(image1: Image.Image | None, image2: Image.Image) -> Image.Image:
    """
    Concatenate two images vertically.

    Args:
        image1 (Image.Image): First image.
        image2 (Image.Image): Second image.

    Returns:
        Image.Image: Concatenated image.
    """
    if image1 is None:
        return image2
    new_image = Image.new("RGBA", (image1.width, image1.height + image2.height))
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (0, image1.height))
    return new_image


def image_concat_horizontally(image1: Image.Image | None, image2: Image.Image) -> Image.Image:
    """
    Concatenate two images horizontally.

    Args:
        image1 (Image.Image): First image.
        image2 (Image.Image): Second image.

    Returns:
        Image.Image: Concatenated image.
    """
    if image1 is None:
        return image2
    new_image = Image.new("RGBA", (image1.width + image2.width, max(image1.height, image2.height)))
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (image1.width, 0))
    return new_image


def generate_card_list_image(card_list: list[Card], with_image: bool) -> Image.Image:
    """
    Generate a list of card images with the specified count, width, and height.

    Args:
        card_list (list[Card]): List of Card objects containing the URL and count.

    Returns:
        Image.Image: Generated card image with the specified count.
    """
    # Create a blank image for the card list
    row_count, colmun_count = calc_row_colmun(len(card_list))
    card_list_image = None
    card_row_image = None
    card_num = row_count * colmun_count
    for i in range(card_num):
        card = card_list[i] if i < len(card_list) else None
        card_image = generate_card_image(card, CARD_WIDHTH, CARD_HEIGHT, with_image)
        card_row_image = image_concat_horizontally(card_row_image, card_image)

        if (i + 1) % colmun_count == 0:
            card_list_image = image_concat_vertically(card_list_image, card_row_image)
            card_row_image = None

    if card_list_image is None:
        card_list_image = card_row_image
    return card_list_image
