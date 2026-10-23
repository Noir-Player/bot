from typing import Sequence

import disnake
from disnake import ui
from disnake.ext import commands
from entities.bot import NoirBot
from entities.config import BotConfig
from entities.config import get_instance as get_config
from entities.node import Node
from entities.node import get_instance as get_node

config: BotConfig = get_config()


class TestCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot

        self.node: Node = get_node()

    @commands.slash_command(
        description="⭐ | Testing!", guild_ids=[config.support_server_id]  # type: ignore
    )
    async def test(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @test.sub_command(name="embed", description="⭐ | Test embed")
    async def embed(self, inter: disnake.ApplicationCommandInteraction):
        components: Sequence[ui.UIComponent] = [
            ui.TextDisplay("test"),
            ui.Separator(),
            ui.Container(
                ui.TextDisplay("this is text inside a container"),
                ui.MediaGallery(
                    disnake.MediaGalleryItem(
                        {
                            "media": {"url": "https://placecats.com/500/600"},
                            "description": "a cool media item",
                        },
                    ),
                    disnake.MediaGalleryItem(
                        {
                            "media": {"url": "https://placecats.com/800/600"},
                            "description": "more kitty",
                            "spoiler": True,
                        },
                    ),
                ),
                ui.Section(
                    ui.TextDisplay(
                        "What an incredible media gallery.\nOkay, that's all the time I've got. I got to get back to playing Animal Crossing New Leaf on my Nintendo 3DS."
                    ),
                    accessory=ui.Thumbnail(
                        media={
                            "url": "https://i.kym-cdn.com/entries/icons/facebook/000/026/585/reggie_animalcrossingtour.jpg"
                        },
                        description="desc",
                    ),
                ),
                ui.Separator(spacing=disnake.SeparatorSpacingSize.large),
                ui.ActionRow(
                    disnake.ui.Button(
                        label="<",
                    ),
                    disnake.ui.Button(label="x", style=disnake.ButtonStyle.primary),
                    disnake.ui.Button(
                        label=">",
                    ),
                ),
                accent_colour=disnake.Colour(0xEE99CC),
                spoiler=True,
            ),
        ]

        await inter.response.send_message(
            components=components, flags=disnake.MessageFlags(is_components_v2=True)
        )


def setup(bot: NoirBot):
    if bot._config.support_server_id:
        bot.add_cog(TestCog(bot))
