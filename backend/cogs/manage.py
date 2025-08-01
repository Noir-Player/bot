import datetime
import os
import sys

import disnake
from _logging import get_logger
from components.embeds import SecondaryEmbed
from disnake.ext import commands
from disnake.utils import _assetbytes_to_base64_data
from entities.bot import NoirBot
from entities.config import BotConfig
from entities.config import get_instance as get_config
from entities.node import Node
from entities.node import get_instance as get_node
from services.persiktunes import Node

config: BotConfig = get_config()
logger = get_logger("manage")


class ManageCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.node: Node = get_node()

    @commands.slash_command(
        name="set", description="🖤 || Manage bot", guild_ids=[config.support_server_id]  # type: ignore
    )
    async def manage(self, _):
        pass

    @manage.sub_command(description="🖤 | Change avatar of bot")
    async def avatar(
        self,
        inter: disnake.ApplicationCommandInteraction,
        image: disnake.Attachment = commands.Param(description="new avatar"),
    ):
        if self.bot.owner_id != inter.author.id:
            raise commands.NotOwner(
                "You don't have permission to use this command", True
            )

        await self.bot.user.edit(avatar=(await image.to_file()).fp.read())

        await inter.send(
            f"Avatar was changed to `{image.filename}`",
            ephemeral=True,
            file=await image.to_file(),
        )

    @manage.sub_command(description="🖤 | Change banner of bot")
    async def banner(
        self,
        inter: disnake.ApplicationCommandInteraction,
        image: disnake.Attachment = commands.Param(description="new banner"),
    ):
        if self.bot.owner_id != inter.author.id:
            raise commands.NotOwner(
                "You don't have permission to use this command", True
            )

        payload = {}
        payload["banner"] = await _assetbytes_to_base64_data(image)  # type: ignore

        await self.bot.user._state.http.edit_profile(payload)

        await inter.send(
            f"Banner was changed to `{image.filename}`",
            ephemeral=True,
            file=await image.to_file(),
        )

    @manage.sub_command(description="🖤 | Change status of bot")
    async def status(
        self,
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param("noirplayer.su", description="Name of status"),
        status: str = commands.Param(
            "idle",
            description="Type of status",
            choices=["online", "idle", "dnd", "invisible"],
        ),
        type: str = commands.Param(
            "listening",
            description="Type of activity",
            choices=["playing", "streaming", "listening", "watching", "custom"],
        ),
    ):
        if self.bot.owner_id != inter.author.id:
            raise commands.NotOwner(
                "You don't have permission to use this command", True
            )

        await self.bot.change_presence(
            status=disnake.Status[status],
            activity=disnake.Activity(name=name, type=disnake.ActivityType[type]),
        )

        await inter.send(f"Status was changed: `{name}` | {type}", ephemeral=True)

    @manage.sub_command(description="🖤🖤 | Execute some command")
    async def execute(
        self,
        inter: disnake.ApplicationCommandInteraction,
        command: str = commands.Param(
            description="command to execute",
            choices=["cogsreload", "stop", "info", "switch", "clear", "reload"],
        ),
    ):
        if self.bot.owner_id != inter.author.id:
            raise commands.NotOwner(
                "You don't have permission to use this command", True
            )

        if command == "cogsreload":
            self.bot.reload_extensions()

        elif command == "help":
            await inter.send(
                """```
                cogsreload - reload all cogs
                stop       - disconnecting bot and close session
                info       - get info from discord
                switch     - switch token
                clear      - clear cache
                reload     - reload bot
                        ```""",
                ephemeral=True,
            )

        elif command == "stop":
            await inter.send("`disconnecting...`", ephemeral=True)
            exit()

        elif command == "clear":
            await inter.response.defer(ephemeral=True)
            self.bot.clear()
            await inter.edit_original_response("`done`")

        elif command == "info":

            # TODO pool stats

            await inter.send(
                f"""```yaml
                    bot name:   {self.bot.user}  | id: {self.bot.user.id}
                    owner:      {self.bot.owner} | id: {self.bot.owner_id}
                    status:     {self.bot.status}
                    limit:      {self.bot.session_start_limit.total if self.bot.session_start_limit else 'unknown'}
                    ============================================
                    guilds:     {len(self.bot.guilds)}
                    users:      {len(self.bot.users)}
                    emojis:     {len(self.bot.emojis)}
                    stickers:   {len(self.bot.stickers)}
                    ============================================
                    LAVALINK STATS
                    nodes:      {1}
                    best node:
                    - ping:     {round(self.node.latency, 3)}
                    - players:  {self.node.player_count}
                    ----------------
                    {datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}
                    ```""",
                ephemeral=True,
            )

        elif command == "reload":
            await inter.send("`reloading`", ephemeral=True)
            os.execv(sys.executable, [sys.executable] + sys.argv)

        elif command == "guilds":
            list = []
            pag = commands.Paginator(prefix="```markdown")

            for guild in self.bot.guilds:
                if not self.node.get_player(guild.id):
                    pag.add_line(f"{guild.name} - {guild.member_count}")
                else:
                    pag.add_line(f"#{guild.name} - {guild.member_count}")

            for page in pag.pages:
                list.append(
                    SecondaryEmbed(
                        title=f"guilds list {pag.pages.index(page)}",
                        description=page,
                    ),
                )

            for embed in list:
                await inter.send(embed=embed, ephemeral=True)

        else:
            await inter.send(
                "`Unknow command. Type 'help' for get info about commands`",
                ephemeral=True,
            )

    @manage.sub_command(
        description="🖤🖤 | Update bot",
    )
    async def update(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        await inter.response.defer(ephemeral=True)
        if self.bot.owner_id != inter.author.id:
            raise commands.NotOwner("You don't have permission to use this command")

        await self.bot.change_presence(
            status=disnake.Status.dnd,
            activity=disnake.Activity(
                type=disnake.ActivityType.playing,
                name=f"Updating to newest version! ✨",
            ),
        )

        for player in list(self.node.players.values()):
            logger.debug(f"player on {player.guild.name} deleted")

            try:
                await player.controller.delete()  # type: ignore
            except BaseException:
                pass

        await self.node.disconnect()
        self.bot.loop.stop()

        os.execv(__file__, sys.argv)

    # TOO DANGEROUS COMMAND.
    # @commands.slash_command(
    #     description="Execute"
    # )
    # async def eval(self, ctx, params: str):
    #     await ctx.response.defer(ephemeral=True)
    #     if self.bot.owner_id != ctx.author.id:
    #         raise commands.NotOwner("You don't have permission to use this command")

    #     await ctx.send(f"Output:\n```python\n{eval(params)}```", ephemeral=True)


def setup(bot: NoirBot):
    if config.support_server_id:
        bot.add_cog(ManageCog(bot))
