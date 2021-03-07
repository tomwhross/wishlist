from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_game", views.add_game, name="add_game"),
    path("games/<str:gamelist>", views.view_gamelist, name="gamelist"),
    path("search/<str:search_entry>", views.search, name="search"),
    path("game/<int:game_id>", views.view_game, name="game"),
    path("star_game/<int:game_id", views.star_game, name="star_game"),
]
