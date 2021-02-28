import json

import requests
import xmltodict
from bs4 import BeautifulSoup
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Game, GameDetails, User

KEY = "0bcdc2b6d79c75d47c698db492d71d613f8e1458"


def index(request):

    search_entry = request.GET.get("q", None)
    import pdb

    pdb.set_trace()
    if search_entry:
        games = Game.objects.filter(title__contains=search_entry).order_by(
            "-current_price"
        )
        search_entry = None

        return render(
            request,
            "xbox/index.html",
            {"wishlist": games},
        )

    return render(
        request,
        "xbox/index.html",
        {"wishlist": Game.objects.filter(user=request.user).order_by("-current_price")},
    )


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "xbox/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "xbox/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "xbox/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "xbox/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "xbox/register.html")


def add_game(request):
    """
    Add a game and its details
    Once a game has been added it can be added to a user's wishlist
    """

    if request.method == "POST":
        url = request.POST["game-url"]
        game = Game.objects.filter(url=url)

        # if the game does not exist and return the game
        # otherwise return the game
        if not game:

            # scrape the game's Xbox Store page
            # and parse the game page title
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            title = (
                soup.title.text.replace("Buy ", "")
                .replace(" - Microsoft Store en-CA", "")
                .replace("™", "")  # TODO: remove this?
                .replace("\u2122", "")
            )

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

            # prepare payload and headers for call to Giantbomb API to get game details
            payload = {
                "api_key": KEY,
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

            giantbomb_game = json.loads(giantbomb_response.content)["results"][0]

            # create the game
            # note if price could not be found, assume $0.00
            try:
                price
            except NameError:
                price = 0

            game = Game(url=url, title=title, user=request.user, current_price=price)
            # TODO: might remove this, currently game added is auto added to user's wishlist
            game.user = request.user
            game.save()

            # add the game details from Giantbomb
            game_details = GameDetails(
                game=game,
                name=giantbomb_game["name"],
                gbid=giantbomb_game["id"],
                guid=giantbomb_game["guid"],
                image=giantbomb_game["image"]["original_url"],
            )
            game_details.save()

        else:
            print("Game exists")

    else:

        return render(
            request,
            "xbox/index.html",
            {
                "wishlist": Game.objects.filter(user=request.user).order_by(
                    "-current_price"
                )
            },
        )
