from django.contrib.auth.models import AbstractUser
from django.db import models

# from django.db.models import Max


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

    @property
    def last_price(self):
        """
        Returns the last recorded price for a game prior to the current price
        """

        return (
            GamePriceHistory.objects.filter(game=self)
            .values("price")
            .annotate(created_at=models.Max("created_at"))
            .order_by("-created_at")[0]["price"]
        )

    @property
    def lowest_price(self):
        """
        Returns the lowest recorded price for a game
        """

        previous_low = (
            GamePriceHistory.objects.filter(game=self)
            .values("price")
            .order_by("price")[0]
        )

        if self.current_price < previous_low["price"]:
            return self.current_price

        return previous_low["price"]

    @property
    def highest_price(self):
        """
        Returns the highest recorded price for a game
        """

        previous_high = (
            GamePriceHistory.objects.filter(game=self)
            .values("price")
            .order_by("-price")[0]
        )

        if self.current_price < previous_high["price"]:
            return self.current_price

        return previous_high["price"]

    @property
    def discount(self):
        return 1 - self.current_price / self.highest_price

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


class GamePriceHistory(models.Model):
    """
    A game can have a history of prices
    Used to help track general price drops
    """

    game = models.ForeignKey(
        "Game", on_delete=models.CASCADE, related_name="price_histories"
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
