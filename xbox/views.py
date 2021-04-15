"""
django views
"""
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Game, GameDetails, GamePriceHistory, User
from .util import (
    InvalidDomain,
    NoPrice,
    get_giantbomb_game_details,
    get_total_pages,
    paginate_list,
    scrape_xbox_store_game_page,
    update_games_price,
)


def index(request):
    """
    Render index
    """

    return render(
        request,
        "xbox/index.html",
    )


def view_gamelist(request, gamelist, page_number=None):
    """
    View for a list of games, e.g. games on sale, games on wishlist
    Handles pagination
    """

    if not page_number:
        page_number = 1

    if gamelist == "wishlist-games":
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Must be logged in to view wishlist"}, status=401
            )
        games = Game.objects.filter(wishlist_users=request.user).order_by(
            "current_price"
        )
    elif gamelist == "sale-games":
        games = Game.objects.filter(noted_sale=True).order_by("current_price")
    else:
        # all games
        games = Game.objects.all()

    games = [game.serialize(request.user) for game in games.order_by("current_price")]

    total_pages = get_total_pages(games)

    games = paginate_list(games, page_number)

    has_next_page = False
    next_page = None
    if page_number < total_pages:
        has_next_page = True
        next_page = page_number + 1

    has_previous_page = False
    previous_page = None
    if page_number > 1:
        has_previous_page = True
        previous_page = page_number - 1

    response = {
        "total_pages": total_pages,
        "current_page": page_number,
        "next_page": next_page,
        "has_next_page": has_next_page,
        "has_previous_page": has_previous_page,
        "previous_page": previous_page or None,
        "games": games,
    }

    return JsonResponse(response)


def view_game(request, game_id):
    """
    Returns a serialized Game object on GET

    If request is PUT, adds or removes from the user's wishlist
    """

    game = Game.objects.get(id=game_id)

    # Add or remove a game from a wishlist
    if request.method == "PUT":

        if request.user.is_authenticated:

            data = json.loads(request.body)
            if data.get("starred") is not None:
                game = Game.objects.get(id=game_id)
                if not request.user in game.wishlist_users.all():
                    game.wishlist_users.add(request.user)
                else:
                    game.wishlist_users.remove(request.user)
                game.save()

        else:
            return JsonResponse(
                {"error": "Must be logged in to add a game to wishlist"}, status=401
            )

    return JsonResponse(game.serialize(request.user))


def view_game_price_history(request, game_id):
    """
    Return a json response of a game's price history
    """

    game = Game.objects.get(id=game_id)
    game_price_history = GamePriceHistory.objects.filter(game=game)

    if game_price_history:
        game_price_history = game_price_history.order_by("-created_at")

        return JsonResponse(
            [entry.serialize() for entry in game_price_history], safe=False
        )

    return JsonResponse([], safe=False)


def search(request, search_entry):
    """
    Search for a game based on the title

    Returns a serialized queryset
    """

    games = Game.objects.filter(title__contains=search_entry)

    return JsonResponse([game.serialize(request.user) for game in games], safe=False)


def login_view(request):
    # import pdb

    # pdb.set_trace()
    if request.method == "POST":

        # Attempt to sign user in
        # username = request.POST["username"]
        username = json.loads(request.body).get("username", None)
        # password = request.POST["password"]
        password = json.loads(request.body).get("password", None)
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return JsonResponse(
                {"user": {"is_authenticated": True}},
                status=200,
            )

    return JsonResponse(
        {"error": "There was a problem logging in"},
        status=400,
    )


# def login_view(request):
#     if request.method == "POST":

#         # Attempt to sign user in
#         username = request.POST["username"]
#         password = request.POST["password"]
#         user = authenticate(request, username=username, password=password)

#         # Check if authentication successful
#         if user is not None:
#             login(request, user)
#             return HttpResponseRedirect(reverse("index"))
#         else:
#             return render(
#                 request,
#                 "xbox/login.html",
#                 {"message": "Invalid username and/or password."},
#             )
#     else:
#         return render(request, "xbox/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = json.loads(request.body).get("username", None)
        email = json.loads(request.body).get("email", None)
        password = json.loads(request.body).get("password", None)
        confirmation = json.loads(request.body).get("confirmation", None)
        if password != confirmation:
            return JsonResponse(
                {"error": "Passwords must match"},
                status=400,
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return JsonResponse(
                {"error": "Username already taken"},
                status=400,
            )
        login(request, user)
    return JsonResponse(
        {"user": {"is_authenticated": True}},
        status=200,
    )


def add_game(request):
    """
    Add a game and its details
    Once a game has been added it can be added to a user's wishlist
    """

    if request.method == "POST":

        url = json.loads(request.body).get("game_url", None)

        if not url:
            return JsonResponse(
                {"error": "Could not add the game, check the URL and try again"},
                status=400,
            )

        games = Game.objects.filter(url=url)

        # if the game does not exist and return the game
        # otherwise return the game

        if not games:
            try:
                xbox_store_page = scrape_xbox_store_game_page(url)
            except InvalidDomain:
                return JsonResponse(
                    {
                        "error": "Not a valid Xbox Store page URL, check the URL and try again"
                    },
                    status=400,
                )
            except NoPrice:
                return JsonResponse(
                    {"error": "Unable to retreive a price for the game"},
                    status=400,
                )

            giantbomb_game_details = get_giantbomb_game_details(
                xbox_store_page["title"]
            )

            # create the game
            game = Game(
                url=url,
                title=xbox_store_page["title"],
                current_price=xbox_store_page["price"],
                regular_price=xbox_store_page["regular_price"],
                regular_price_available=xbox_store_page["regular_price_available"],
                discount=xbox_store_page["discount"],
                days_left_on_sale=xbox_store_page["days_left_on_sale"],
                noted_sale=xbox_store_page["noted_sale"],
                noted_sale_type=xbox_store_page["noted_sale_type"],
                on_gamepass=xbox_store_page["on_gamepass"],
            )
            game.save()  # setting id is required before adding ManyToMany relationships

            # add the game details from Giantbomb
            game_details = GameDetails(
                game=game,
                name=giantbomb_game_details["name"],
                gbid=giantbomb_game_details["id"],
                guid=giantbomb_game_details["guid"],
                image=giantbomb_game_details["image"]["original_url"],
            )
            game_details.save()

        else:
            print("Game exists, updating")

            update_games_price(games)

            if request.user.is_authenticated:

                _ = [game.wishlist_users.add(request.user) for game in games]

    return JsonResponse({"game_id": game.id})
