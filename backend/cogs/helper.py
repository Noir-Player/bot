import disnake
from components import PrimaryEmbed
from components.embeds.logs import GuildJoinLogEmbed, GuildLeaveLogEmbed
from disnake.ext import commands
from entities.bot import NoirBot
from entities.config import BotConfig
from entities.config import get_instance as get_config
from entities.node import Node
from entities.node import get_instance as get_node


class HelpCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot

        self.config: BotConfig = get_config()

        self.node: Node = get_node()

    # ---------------------------------------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild):
        if not self.config.logs_channel_id:
            return

        log = await self.bot.fetch_channel(self.config.logs_channel_id)

        await log.send(embed=GuildJoinLogEmbed(guild))  # type: ignore

    # ---------------------------------------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: disnake.Guild):
        if not self.config.logs_channel_id:
            return

        log = await self.bot.fetch_channel(self.config.logs_channel_id)

        await log.send(embed=GuildLeaveLogEmbed(guild))  # type: ignore

        try:
            await self.node.get_player(guild.id).destroy()
        except BaseException:
            pass

    # ---------------------------------------------------------------------------------------------------------

    @commands.slash_command(description="⭐ | Need some help?")
    async def help(self, inter: disnake.ApplicationCommandInteraction):

        embed = PrimaryEmbed(
            description="You can find out more about **Noir Player** below 👇",
        )

        await inter.send(
            embed=embed,
            ephemeral=True,
            components=[
                disnake.ui.Button(
                    label="Documentation", url="https://docs.noirplayer.su/"
                )
            ],
        )


def setup(bot: NoirBot):

    bot.add_cog(HelpCog(bot))
