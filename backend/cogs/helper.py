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

        log = await self.bot.fetch_channel(self.config.logs_channel_id)

        await log.send(embed=GuildJoinLogEmbed(guild))

    # ---------------------------------------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: disnake.Guild):
        log = await self.bot.fetch_channel(self.config.logs_channel_id)
        await log.send(
            embed=GuildLeaveLogEmbed(guild),
        )

        try:
            await self.node.get_player(guild.id).destroy()
        except BaseException:
            pass

    # ---------------------------------------------------------------------------------------------------------

    @commands.slash_command(description="⭐ | нужна помощь?")
    async def help(self, inter: disnake.ApplicationCommandInteraction):

        embed = PrimaryEmbed(
            title="Нужна помощь?",
            description="Посетите документацию **Noir Player** 👇",
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


def setup(bot: commands.Bot):

    bot.add_cog(HelpCog(bot))
