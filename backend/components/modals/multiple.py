import disnake


class AddMultipleModal(disnake.ui.Modal):
    def __init__(
        self,
        player,
        *,
        title: str = "Add multiple tracks",
        custom_id: str = "add_multiple_modal",
        timeout: float = 600,
    ) -> None:
        self.player = player

        components = [
            disnake.ui.TextInput(
                label="You can provide urls or search queries",
                placeholder="rickroll\nGambare remix\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ",
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
