from components.modals.eval import EvalModal
from disnake import ApplicationCommandInteraction
from disnake.ext import commands
from entities.bot import NoirBot
from entities.config import get_instance as get_config

config = get_config()


class EvalCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        pass

    @commands.slash_command(name="eval_multiple", guild_ids=[config.support_server_id])
    async def eval_multiple(self, interaction: ApplicationCommandInteraction):
        if interaction.author.id == self.bot.owner_id:
            await interaction.response.send_modal(EvalModal())
        else:
            raise commands.NotOwner("Вы не можете пользоваться этой командой")


def setup(bot: commands.Bot):
    bot.add_cog(EvalCog(bot))
