"""
general utilities
"""

import json
import os
import re

import requests
from bs4 import BeautifulSoup

from .models import Game, GamePriceHistory


def scrape_xbox_store_game_page(url):
    """
    Scrape the Xbox Store game page for a given url
    returns a game title and current price
    """

    # scrape the game's Xbox Store page
    # and parse the game page title
    price = None
    noted_sale = False
    noted_sale_type = None

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    title = (
        soup.title.text.replace("Buy ", "")
        .replace(" - Microsoft Store en-CA", "")
        .replace("™", "")  # TODO: remove this?
        .replace("\u2122", "")
    )

    # there are different ways the Xbox Store page will store regular and sale
    # price data

    # this is an Xbox Gold sale price retreival
    xbox_gold_sale_price_containers = soup.find_all(
        "div", {"class": "remediation-cta-label"}
    )
    if xbox_gold_sale_price_containers:
        try:
            price = re.findall(r"\d+\.\d+", xbox_gold_sale_price_containers[0].text)[0]
        except IndexError:
            price = 0
        else:
            noted_sale = True
            noted_sale_type = "Xbox Gold Sale"

    publisher_sale_price_containers = soup.find_all(
        "span", {"class": "price-disclaimer"}
    )
    if publisher_sale_price_containers:
        price = re.findall(r"\d+\.\d+", publisher_sale_price_containers[0].text)[0]
        noted_sale = True
        noted_sale_type = "Publisher Sale"

    # if no Xbox Gold sale price was retrieved, get the current regular price
    if not price:

        # this is the prefix of current element that contains the current price
        # subject to change without warning!
        price_element_id_prefix = "ProductPrice_productPrice_PriceContainer-"

        # the price container element changes throughout the day
        # currently, only the number suffix changes
        # have seen as high as 11, but trying 50
        for i in range(0, 50):
            price_element_id = f"{price_element_id_prefix}{i}"
            price_element = soup.find(id=price_element_id)

            try:
                price_element_text = price_element.text
            except AttributeError:
                continue
            else:
                # once the price text has been located, parse out the decimal price
                price = price_element_text.replace("CAD $", "").replace(
                    "+Offers in-app purchases", ""
                )
                break

    return {
        "title": title,
        "price": price or 0,
        "noted_sale": noted_sale,
        "noted_sale_type": noted_sale_type,
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
        xbox_store_game_details = scrape_xbox_store_game_page(game.url)

        if xbox_store_game_details["price"] != str(game.current_price):
            game_price_history = GamePriceHistory(game=game, price=game.current_price)
            game.current_price = xbox_store_game_details["price"]
            game.noted_sale = xbox_store_game_details["noted_sale"]
            game.noted_sale_type = xbox_store_game_details["noted_sale_type"]

            game_price_history.save()
            game.save()

    return games


def get_giantbomb_api_key():
    """
    Calling the Giantbomb API requires a secret key
    Key needs to be set as an environment variabe called GIANTBOMB_API_KEY
    E.g. export GIANTBOMB_API_KEY=<my_secret_key>
    """

    return os.getenv("GIANTBOMB_API_KEY")


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

    return json.loads(giantbomb_response.content)["results"][0]
