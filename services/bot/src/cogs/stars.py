from components.embeds import PrimaryEmbed, SecondaryEmbed
from components.views.playlist import EmbedPlaylist
from disnake.ext import commands
from entities.bot import NoirBot
from entities.node import Node
from entities.node import get_instance as get_node
from exceptions import *
from services.database.models.star import StarDocument
from validators.player import check_player


class StarsCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.node: Node = get_node()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Избранные

    # TODO: Database

    @commands.slash_command(name="stars")
    @commands.contexts(guild=True, private_channel=True)
    async def star(self, _):
        pass

    @star.sub_command(description="💖 | Your starred tracks")
    async def open(
        self,
        ctx,
        hidden: int = commands.Param(
            default=0,
            description="Must I show it to you only?",
            choices=[
                disnake.OptionChoice(name="Yes", value=1),
                disnake.OptionChoice(name="No", value=0),
            ],
        ),
    ):
        await ctx.response.defer(ephemeral=bool(hidden))

        stars = await StarDocument.find_one(StarDocument.user_id == ctx.author.id)

        if not stars or not stars.tracks:
            return await ctx.edit_original_message(
                embed=SecondaryEmbed(
                    title="You don't have any starred tracks",
                    description="You can star tracks using `/star add` command 💖.",
                )
            )

        if stars.tracks:
            await EmbedPlaylist(node=self.node, playlist=stars).send(ctx=ctx)

    @check_player()
    @star.sub_command(description="💖 | Star current track")
    async def add(self, ctx):
        player = self.node.get_player(ctx.guild_id)

        stars = await StarDocument.find_one(
            StarDocument.user_id == ctx.author.id
        ) or StarDocument(user_id=ctx.author.id)

        if not player.current:  # type: ignore
            raise NoCurrent("There is no current track to star 💔")

        if not player.current.info.isStream and not next((obj for obj in stars.tracks if obj.info.uri == player.current.info.uri), None):  # type: ignore
            track = player.current  # type: ignore

            await ctx.send(
                embed=PrimaryEmbed(
                    description=f"Track `{track.info.title}` added to stars! 💖"
                )
            )
            stars.tracks.append(
                track.model_copy(update={"ctx": None, "requester": None})
            )

            await stars.save()

        else:
            return await ctx.delete_original_message()


def setup(bot: NoirBot):
    bot.add_cog(StarsCog(bot))
