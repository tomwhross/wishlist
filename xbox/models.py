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

    # user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="games")
    wishlist_users = models.ManyToManyField("User", blank=True, related_name="wishlist")
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
        if self.noted_sale:
            return f"{self.title} is on sale for ${self.current_price}"

        return f"{self.title} is not on sale, at ${self.current_price}"

    @property
    def regular_price(self):
        """
        Returns the last recorded price for a game prior to the current price
        """

        if not self.noted_sale:
            return self.current_price

        historical_regular_price = (
            GamePriceHistory.objects.filter(game=self, noted_sale=False)
            .order_by("-created_at")
            .first()
        )

        if historical_regular_price:
            return historical_regular_price.price

        return "New entry on sale, unknown regular price"

    @property
    def lowest_price(self):
        """
        Returns the lowest recorded price for a game
        """

        previous_low = (
            GamePriceHistory.objects.filter(game=self).order_by("price").first()
        )

        if previous_low:
            return previous_low.price

        return 0.00

    @property
    def discount(self):
        """
        Return a discount percentage if there is a sale
        """
        if self.noted_sale and not isinstance(self.regular_price, str):
            return 1 - self.current_price / self.regular_price

        return 0

    def is_wishlist_user(self, user=None):
        """
        Check is the game is on a user's wishlist
        """

        if not user:
            return False

        if user in self.wishlist_users.filter(id=user.id):
            return True

        return False

    def serialize(self, user=None):
        """
        Serialize the Game model for fetch response in js
        """

        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "is_wishlist_user": self.is_wishlist_user(user),
            "current_price": f"${str(self.current_price)}",
            "noted_sale": self.noted_sale,
            "noted_sale_type": self.noted_sale_type,
            "created_at": self.created_at.strftime("%b %-d %Y, %-I:%M %p"),
            "regular_price": self.regular_price,
            "lowest_price": self.lowest_price,
            "discount": self.discount,
            "image": self.details.first().image,
        }


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
    noted_sale = models.BooleanField(blank=False)
    noted_sale_type = models.TextField(
        max_length=255, blank=True, null=True, default=None
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
