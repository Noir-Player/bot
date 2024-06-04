import disnake

import services.persiktunes as persik


class AddMultiple(disnake.ui.Modal):
    """Modal добавить несколько"""

    def __init__(
        self,
        player,
        *,
        title: str = "Добавить несколько элементов",
        custom_id: str = "add_multiple_modal",
        timeout: float = 600,
    ) -> None:
        self.player = player

        components = [
            disnake.ui.TextInput(
                label="Названия/ссылки через строку",
                placeholder="rickroll\nGambare remix",
                custom_id="sounds",
                style=disnake.TextInputStyle.long,
            )
        ]

        super().__init__(
            title=title, components=components, custom_id=custom_id, timeout=timeout
        )

    async def callback(self, inter):
        await inter.response.defer(ephemeral=True)

        values = str(list(inter.text_values.values())[0])

        for query in values.split("\n"):
            result = await self.player.node.rest.abstract_search.search(
                query=query,
                ctx=inter,
                requester=inter.author.display_name,
            )

            success = await self.player.queue.put_auto(result)

            if not self.player.current and success:
                await self.player.play(self.player.queue.get())

        await inter.delete_original_response()
