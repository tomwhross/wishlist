from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Game(models.Model):
    """
    A game entry with a URL to the store page
    A user can add a game to their wishlist, and a game
    can exist without being on a wishlist
    """

    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="games")
    title = models.TextField(max_length=500, blank=False)
    url = models.TextField(max_length=1000, blank=False)
    current_price = models.DecimalField(max_digits=6, decimal_places=2)
    noted_sale = models.BooleanField(blank=False)
    noted_sale_type = models.TextField(
        max_length=255, blank=True, null=True, default=None
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"

    # @property
    # def user_count(self):
    #     """
    #     A count of how many users have a game on their wishlist
    #     """
    #     return self.user.count()


class GameDetails(models.Model):
    """
    A game can have details like an image and a generic title
    Largely populated via the GiantBomb API https://www.giantbomb.com/api/
    """

    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name="details")
    name = models.TextField(max_length=500, blank=False)
    gbid = models.IntegerField()
    guid = models.TextField(max_length=255)
    image = models.TextField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    # @property
    # def user_count(self):
    #     """
    #     A count of how many users have a game on their wishlist
    #     """
    #     return self.user.count()
