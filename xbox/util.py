"""
general utilities
"""

import json
import os
import re

import requests
from bs4 import BeautifulSoup

from .constants import SEED_URLS
from .models import Game, GamePriceHistory


class MissingEnvironmentVariable(Exception):
    """
    Exception for missing env var
    """


class InvalidDomain(Exception):
    """
    Exception for non-Xbox game store pages
    """


class NoPrice(Exception):
    """
    Exception if the scraper is unable to retreive a price
    """


def seed_games():
    """
    Seeds the database with an initial set of games
    """

    for url in SEED_URLS:
        scrape_xbox_store_game_page(url)


def get_game_page(url):
    """
    Get the HTML for a given URL, where the URL is a game's page in the Xbox
    Store
    """

    try:
        response = requests.get(url)
    except (requests.exceptions.MissingSchema, ConnectionError):
        return None

    game_page = BeautifulSoup(response.content, "html.parser")

    return game_page


def get_game_page_title(game_page):
    """
    Extracts the game's title from an Xbox Store game page
    """

    # get the game title from the HTML title tag
    #   and strip unncessary characters
    title = game_page.title.text.replace("Buy ", "").replace(
        " - Microsoft Store en-CA", ""
    )

    return title


def is_on_gamepass(game_page):
    """
    Check if a game is on Game Pass given its game page from the store
    """

    game_pass_ultimate_label = "Included with Xbox Game Pass Ultimate"
    ea_play_label = "Included with EA Play"

    if game_pass_ultimate_label in game_page.text or ea_play_label in game_page.text:
        return True

    return False


def is_gold_sale(game_page):
    """
    Check if a sale if for Gold subscribers only
    """

    gold_labels = ["with Xbox Live Gold", "Go Gold"]
    for gold_label in gold_labels:
        if gold_label not in game_page.text:
            return False

    return True


def get_publisher_sale_price(game_page):
    """
    Check is sale is publisher sale and if it is get and return the sale price
    """

    publisher_sale_price_containers = game_page.find_all(
        "span", {"class": "price-disclaimer"}
    )
    if publisher_sale_price_containers:
        return re.findall(r"\d+\.\d+", publisher_sale_price_containers[0].text)[0]

    return None


def get_publisher_sale_regular_price(game_page):
    """
    Check if sale is publisher sale and if it is get and return the regular price
    """

    publisher_sale_regular_price_containers = game_page.find_all(
        "s", {"aria-hidden": "true"}
    )

    if publisher_sale_regular_price_containers:
        try:

            return re.findall(
                r"\d+\.\d+", publisher_sale_regular_price_containers[0].text
            )[0]
        except IndexError:

            return None


def get_gold_sale_price(game_page):
    """
    Check if a sale is a Gold sale and if it is get and return the current sale price
    """

    # this is an Xbox Gold sale price retreival
    xbox_gold_sale_price_containers = game_page.find_all(
        "div", {"class": "remediation-cta-label"}
    )

    if not xbox_gold_sale_price_containers:
        return None

    try:
        return re.findall(r"\d+\.\d+", xbox_gold_sale_price_containers[0].text)[0]
    except IndexError:
        return None


def get_discount(game_page):
    """
    Returns a discount percentage if available
    """

    discount_containers = game_page.find_all("span", {"class": "sub"})
    if discount_containers:
        try:
            discount_sub_container = re.findall(
                r"[0-9]*\% off", discount_containers[0].text
            )[0]

            return re.findall(r"\d+", discount_sub_container)[0]
        except IndexError:

            return None

    return None


def get_days_left_on_sale(game_page):
    """
    Returns the number of days left on sale if available
    """

    days_left_on_sale_containers = game_page.find_all(
        "span", {"class": "caption text-muted", "aria-live": "polite"}
    )

    if days_left_on_sale_containers:
        try:
            days_left_on_sale = re.findall(
                r"\d+.days?.left", str(days_left_on_sale_containers[0])
            )

            return re.findall(r"\d+", days_left_on_sale[0])[0]

        except IndexError:

            return None

    return None


def get_regular_price(game_page):
    """
    Get and return the regular price of a game
    """

    regular_price = None
    price_element_id_prefix = "ProductPrice_productPrice_PriceContainer-"

    # the price container element changes throughout the day
    # currently, only the number suffix changes
    # have seen as high as 11, but trying 50
    for i in range(0, 50):
        price_element_id = f"{price_element_id_prefix}{i}"
        price_element = game_page.find(id=price_element_id)

        try:
            price_element_text = price_element.text
        except AttributeError:
            continue
        else:
            # once the price text has been located, parse out the decimal price
            regular_price = price_element_text.replace("CAD $", "").replace(
                "+Offers in-app purchases", ""
            )
            break

    return regular_price


def get_game_prices(game_page):
    """
    Scrape the page to get the current price and the regular price if the
    current price is a sale price
    """

    publisher_sale_price = get_publisher_sale_price(game_page)
    publisher_sale_regular_price = get_publisher_sale_regular_price(game_page)

    if publisher_sale_price and publisher_sale_regular_price:
        return publisher_sale_price, publisher_sale_regular_price

    xbox_gold_sale_price = get_gold_sale_price(game_page)
    regular_price = get_regular_price(game_page)

    if xbox_gold_sale_price and regular_price:
        return xbox_gold_sale_price, regular_price

    # game is not on sale
    return regular_price, regular_price


def scrape_xbox_store_game_page(url):
    """
    Scrape the Xbox Store game page for a given url
    returns a game title and current price
    """

    if "microsoft.com/en-ca/" not in url.lower():
        raise InvalidDomain

    # scrape the game's Xbox Store page
    # and parse the game page title
    noted_sale = False
    noted_sale_type = None

    game_page = get_game_page(url)
    if not game_page:
        return None

    price, regular_price = get_game_prices(game_page)

    if price == 0 and regular_price == 0:
        raise NoPrice

    gold_sale = is_gold_sale(game_page)
    if gold_sale:
        noted_sale_type = "Xbox Gold Sale"
        noted_sale = True

    if price != regular_price and not noted_sale:
        noted_sale = True
        noted_sale_type = "Publisher Sale"

    return {
        "title": get_game_page_title(game_page),
        "price": price or 0,
        "noted_sale": noted_sale,
        "noted_sale_type": noted_sale_type,
        "on_gamepass": is_on_gamepass(game_page),
        "regular_price": regular_price,
        "regular_price_available": bool(regular_price),
        "discount": get_discount(game_page),
        "days_left_on_sale": get_days_left_on_sale(game_page),
    }


def check_if_game_on_wishlist(games, user):

    for game in games:
        if user in game.wishlist_users:
            game.on_wishlist = True

    return games


def update_games_price(games):
    """
    Takes a set of game objects and updates the price if the current price in
    the Xbox Store is different that the currently stored price in the app
    """

    for game in games:

        xbox_store_page = scrape_xbox_store_game_page(game.url)

        if xbox_store_page["price"] != str(game.current_price):
            game_price_history = GamePriceHistory(
                game=game,
                price=game.current_price,
                noted_sale=game.noted_sale,
                noted_sale_type=game.noted_sale_type,
            )

            game_price_history.save()

        game.current_price = xbox_store_page["price"]
        game.noted_sale = xbox_store_page["noted_sale"]
        game.noted_sale_type = xbox_store_page["noted_sale_type"]
        game.on_gamepass = xbox_store_page["on_gamepass"]
        game.regular_price = xbox_store_page["regular_price"]
        game.regular_price_available = xbox_store_page["regular_price_available"]
        game.discount = xbox_store_page["discount"]
        game.days_left_on_sale = xbox_store_page["days_left_on_sale"]

        game.save()

    return games


def get_giantbomb_api_key():
    """
    Calling the Giantbomb API requires a secret key
    Key needs to be set as an environment variabe called GIANTBOMB_API_KEY
    E.g. export GIANTBOMB_API_KEY=<my_secret_key>
    """

    giant_bomb_key = os.getenv("GIANTBOMB_API_KEY")

    if not giant_bomb_key:
        raise MissingEnvironmentVariable(
            "Environment variable `GIANTBOMB_API_KEY` not found"
        )

    return giant_bomb_key


def get_giantbomb_game_details(title):
    """
    Search the Giantbomb API for a given game title
    returns Giantbomb title, image url, and ids for future lookups
    """

    # prepare payload and headers for call to Giantbomb API to get game details
    payload = {
        "api_key": get_giantbomb_api_key(),
        "format": "json",
        "query": title,
        "resource": "game",
        "field_list": "id,guid,name,image",
    }
    headers = {"User-Agent": "Xbox Wishlist App"}

    # searching Giantbomb for the game
    # currently their search is very good so assuming the first result
    # is the game we're looking for
    giantbomb_response = requests.get(
        "https://www.giantbomb.com/api/search/",
        params=payload,
        headers=headers,
    )

    # arbitrarily picking the first result
    return json.loads(giantbomb_response.content)["results"][0]


def paginate_list(items, page_number):
    """
    returns a sliced list of a list for pagination
    """

    items_per_page = 12

    start = (page_number - 1) * items_per_page
    end = page_number * items_per_page

    paginated_items = items[start:end]

    return paginated_items


def get_total_pages(items):
    """
    returns the total number of pages for a list of serialized items
    """

    items_per_page = 12

    if len(items) % items_per_page == 0:
        return int(len(items) / items_per_page)

    pages = int(len(items) / items_per_page + 1)

    return pages
