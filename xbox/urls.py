from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_game", views.add_game, name="add_game"),
    path(
        "games/<str:gamelist>/<int:page_number>", views.view_gamelist, name="gamelist"
    ),
    path("games/<str:gamelist>", views.view_gamelist, name="gamelist"),
    path("search/<str:search_entry>", views.search, name="search"),
    path("game/<int:game_id>", views.view_game, name="game"),
    path("prices/<int:game_id>", views.view_game_price_history, name="prices"),
]
