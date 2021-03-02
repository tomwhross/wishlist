from django.contrib import admin

from .models import Game, GameDetails, GamePriceHistory, User

admin.site.register(User)
admin.site.register(Game)
admin.site.register(GameDetails)
admin.site.register(GamePriceHistory)
