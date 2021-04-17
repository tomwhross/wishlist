import kronos
from django.core.management.base import BaseCommand, CommandError
from xbox.models import Game
from xbox.util import InvalidDomain, NoPrice, update_games_price


# automatically run task to update all game prices every 8 hours on the hour
@kronos.register("0 */8 * * *")
class Command(BaseCommand):
    help = "Updates game prices, sale info, and price history"

    def add_arguments(self, parser):
        parser.add_argument(
            "--game_ids",
            type=int,
            nargs="+",
            help="Pass a specific list of game IDs to update, e.g. --game_ids 17 22 23",
        )

    def handle(self, *args, **options):
        if not options["game_ids"]:
            games = Game.objects.all()
        else:
            games = []
            for game_id in options["game_ids"]:
                try:
                    game = Game.objects.get(pk=game_id)
                except Game.DoesNotExist:
                    raise CommandError(f'Game "{game_id}" does not exist')
                games.append(game)

        update_games_price(games)

        if len(games) == 1:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated game "{[game.id for game in games]}"'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated games "{[game.id for game in games]}"'
                )
            )
