import configparser
import datetime
import os
import sys

import disnake
from disnake.ext import commands
from disnake.utils import _assetbytes_to_base64_data

from helpers.embeds import genembed
from objects.bot import NoirBot
from services.persiktunes import Node

config = configparser.ConfigParser()
config.read("noir.properties")


class Manage(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.pool = bot.pool

    @commands.slash_command(guild_ids=[config.getint("dev", "dev_server")])
    async def set_avatar(
        self,
        ctx,
        image: disnake.Attachment = commands.Param(description="сменить аватар боту"),
    ):
        await self.bot.user.edit(avatar=(await image.to_file()).fp.read())

        await ctx.send(
            f"Аватар сменен: {image.filename}",
            ephemeral=True,
            file=await image.to_file(),
        )

    @commands.slash_command(guild_ids=[config.getint("dev", "dev_server")])
    async def set_banner(
        self,
        ctx,
        image: disnake.Attachment = commands.Param(description="сменить баннер боту"),
    ):
        payload = {}
        payload["banner"] = await _assetbytes_to_base64_data(image)

        data = await self.bot.user._state.http.edit_profile(payload)

        await ctx.send(
            f"Аватар сменен: {image.filename}",
            ephemeral=True,
            file=await image.to_file(),
        )

    @commands.slash_command(guild_ids=[config.getint("dev", "dev_server")])
    async def set_status(
        self,
        ctx,
        name: str = commands.Param("noirplayer.su", description="Имя статуса"),
        status: str = commands.Param(
            "idle",
            description="Тип статуса",
            choices=["online", "idle", "dnd", "invisible"],
        ),
        type: str = commands.Param(
            "listening",
            description="Тип активности",
            choices=["playing", "streaming", "listening", "watching", "custom"],
        ),
    ):
        await self.bot.change_presence(
            status=disnake.Status[status],
            activity=disnake.Activity(name=name, type=disnake.ActivityType[type]),
        )

        await ctx.send(f"Статус сменен: {name} [{type}]", ephemeral=True)

    @commands.slash_command(guild_ids=[config.getint("dev", "dev_server")])
    async def manage(self, ctx, prompt: str = commands.Param(description="параметр")):
        if ctx.author == self.bot.user:
            return

        if self.bot.owner_id != ctx.author.id:
            raise commands.NotOwner("не дев")

        if prompt == "cogsreload":
            self.bot.exreload()

        elif prompt == "help":
            await ctx.send(
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

        elif prompt == "stop":
            await ctx.send("`disconnecting...`", ephemeral=True)
            exit()

        elif prompt == "clear":
            await ctx.send("`clearing...`", ephemeral=True)
            self.bot.clear()
            await ctx.send("`done`", ephemeral=True)

        elif prompt == "info":
            node: Node = self.bot.node

            await ctx.send(
                f"""```yaml
bot name:   {self.bot.user}  | id: {self.bot.user.id}
owner:      {self.bot.owner} | id: {self.bot.owner_id}
status:     {self.bot.status}
limit:      {self.bot.session_start_limit.reset_time}
============================================
guilds:     {len(self.bot.guilds)}
users:      {len(self.bot.users)}
emojis:     {len(self.bot.emojis)}
stickers:   {len(self.bot.stickers)}
============================================
LAVALINK STATS
nodes:      {self.pool.node_count}
best node:
- ping:     {round(node.latency, 3)}
- players:  {node.player_count}
- os stats:
- - uptime: {node.stats.uptime}
- - used:   {node.stats.used}
- - load:   {node.stats.cpu_system_load}
----------------
{datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}
            ```""",
                ephemeral=True,
            )

        elif prompt == "reload":
            await ctx.send("`reloading`", ephemeral=True)
            os.execv(sys.executable, [sys.executable] + sys.argv)

        elif prompt == "guilds":
            node: Node = self.bot.node
            list = []
            pag = commands.Paginator(prefix="```markdown")

            for guild in self.bot.guilds:
                if not node.get_player(guild.id):
                    pag.add_line(f"{guild.name} - {guild.member_count}")
                else:
                    pag.add_line(f"#{guild.name} - {guild.member_count}")

            for page in pag.pages:
                list.append(
                    genembed(f"guilds list {pag.pages.index(page)}", description=page)
                )

            for embed in list:
                await ctx.send(embed=embed, ephemeral=True)

        else:
            await ctx.send(
                "`unknow command. Type 'help' for get info about commands`",
                ephemeral=True,
            )

    @commands.slash_command(
        description="Выпустить обновление",
        guild_ids=[config.getint("dev", "dev_server")],
    )
    async def update(self, ctx):
        await ctx.response.defer(ephemeral=True)
        if self.bot.owner_id != ctx.author.id:
            raise commands.NotOwner("Вы не можете пользоваться этой командой")

        await self.bot.change_presence(
            status=disnake.Status.dnd,
            activity=disnake.Activity(
                type=disnake.ActivityType.playing, name=f"Обновляется"
            ),
        )

        for player in list(self.bot.node.players.values()):
            self.bot._log.debug(f"player on {player.guild.name} deleted")

            try:
                await player.controller.delete()
            except BaseException:
                pass

        await self.pool.disconnect()

        self.bot.loop.stop()

        os.execv(__file__, sys.argv)

    @commands.slash_command(
        description="Выполнить", guild_ids=[config.getint("dev", "dev_server")]
    )
    async def eval(self, ctx, params: str):
        await ctx.response.defer(ephemeral=True)
        if self.bot.owner_id != ctx.author.id:
            raise commands.NotOwner("Вы не можете пользоваться этой командой")

        await ctx.send(f"Вывод:\n```python\n{eval(params)}```", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Manage(bot))
