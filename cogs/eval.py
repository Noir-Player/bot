from disnake.ext import commands
from disnake.interactions.modal import ModalInteraction
from disnake.ui import Modal

from classes.Bot import NoirBot

from utils.printer import *

import disnake


class EvalModal(Modal):
    def __init__(self, bot, pool) -> None:
        self.bot = bot
        self.pool = pool

        components = [
            disnake.ui.TextInput(
                label="Параметры",
                custom_id="params",
                style=disnake.TextInputStyle.paragraph,
            )
        ]

        super().__init__(
            title="Выполнить",
            components=components,
            custom_id="eval_modal",
            timeout=600,
        )

    async def callback(self, interaction: ModalInteraction):
        await interaction.response.defer(ephemeral=True)

        output, i = "", 1

        for line in interaction.text_values["params"].split("\n"):
            try:
                out = eval(line)
            except Exception as e:
                out = f"Error: {e}"

            lprint(out, Color.blue, "EVAL")
            output += f"[{i}] {out}\n"

            i += 1

        await interaction.send(f"## Вывод в консоли:\n```py\n{output}\n```")


class Eval(commands.Cog):  # Not enabled
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.pool = bot.pool

    @commands.slash_command(name="eval_multiple",
                            guild_ids=[939582886305230849])
    async def eval_multiple(self, ctx):
        if ctx.author.id == self.bot.owner_id:
            await ctx.response.send_modal(EvalModal(self.bot, self.pool))
        else:
            await ctx.send("Хуй тебе")


def setup(bot: commands.Bot):
    bot.add_cog(Eval(bot))
