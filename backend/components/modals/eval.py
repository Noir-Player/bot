import disnake
from disnake.interactions.modal import ModalInteraction
from disnake.ui import Modal


class EvalModal(Modal):
    def __init__(self) -> None:

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

            self.bot._log.debug(out)
            output += f"[{i}] {out}\n"

            i += 1

        await interaction.send(f"## Вывод в консоли:\n```py\n{output}\n```")
