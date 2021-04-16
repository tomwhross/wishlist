from django.core.management.base import BaseCommand, CommandError
from xbox.constants import SEED_URLS
from xbox.models import Game, GameDetails, GamePriceHistory
from xbox.util import (
    get_giantbomb_game_details,
    scrape_xbox_store_game_page,
    update_games_price,
)


class Command(BaseCommand):
    help = "Seeds the database with a small number of games"

    def handle(self, *args, **options):

        for url in SEED_URLS:
            games = Game.objects.filter(url=url)

            if not games:
                try:
                    xbox_store_page = scrape_xbox_store_game_page(url)
                except InvalidDomain:
                    raise CommandError(f'URL "{url}" is not a valid Xbox Store URL')
                except NoPrice:
                    raise CommandError(f'Could not find a game price on page "{url}"')

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

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully inserted {game.title} from "{url}"'
                    )
                )

            else:
                # case - game already existed in the db
                update_games_price(games)

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully updated {[game.title for game in games]} from "{url}"'
                    )
                )
