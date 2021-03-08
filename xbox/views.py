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

from .models import Game, GameDetails, User
from .util import (
    check_if_game_on_wishlist,
    get_giantbomb_game_details,
    scrape_xbox_store_game_page,
    update_games_price,
)


def index(request):
    if request.user.is_authenticated:

        # TODO: this should be a post request
        search_entry = request.GET.get("q", None)

        if search_entry:
            games = Game.objects.filter(title__contains=search_entry).order_by(
                "-current_price"
            )

            return render(
                request,
                "xbox/index.html",
                {"wishlist": games},
            )

        return render(
            request,
            "xbox/index.html",
            {
                "wishlist": Game.objects.filter(wishlist_users=request.user).order_by(
                    "-current_price"
                )
            },
        )

    # return HttpResponseRedirect(reverse("login"))

    return render(
        request,
        "xbox/index.html",
    )


# @login_required
def view_gamelist(request, gamelist):

    if gamelist == "wishlist-games":
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Must be logged in to view wishlist"}, status=401
            )
        games = Game.objects.filter(wishlist_users=request.user).order_by(
            "-current_price"
        )
    elif gamelist == "sale-games":
        games = Game.objects.filter(noted_sale=True).order_by("-current_price")
    else:
        # all games
        games = Game.objects.all()

    return JsonResponse([game.serialize(request.user) for game in games], safe=False)


def view_game(request, game_id):

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


def search(request, search_entry):

    games = Game.objects.filter(title__contains=search_entry)

    return JsonResponse([game.serialize(request.user) for game in games], safe=False)


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
        games = Game.objects.filter(url=url)

        # if the game does not exist and return the game
        # otherwise return the game

        if not games:
            xbox_store_page = scrape_xbox_store_game_page(url)

            giantbomb_game_details = get_giantbomb_game_details(
                xbox_store_page["title"]
            )

            # create the game

            game = Game(
                url=url,
                title=xbox_store_page["title"],
                current_price=xbox_store_page["price"],
                noted_sale=xbox_store_page["noted_sale"],
                noted_sale_type=xbox_store_page["noted_sale_type"],
            )
            game.save()  # setting id is required before adding ManyToMany relationships

            # TODO: might remove this, currently game added is auto added to user's wishlist
            game.wishlist_users.add(request.user)

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

            _ = [game.wishlist_users.add(request.user) for game in games]

    return HttpResponseRedirect(reverse("index"))
