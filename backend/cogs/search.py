from disnake.ext import commands

import services.persiktunes as persik
from objects.bot import NoirBot
from objects.exceptions import *
from objects.player import NoirPlayer
from validators.player import check_player_decorator


class SearchCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.pool = bot.pool


def setup(bot: commands.Bot):
    bot.add_cog(SearchCog(bot))
