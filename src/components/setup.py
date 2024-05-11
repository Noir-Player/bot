import disnake
from disnake.interactions.modal import ModalInteraction

from services.database.core import Database

db = Database().setup

options = []

desc = [
    ["Права", "Кто сможет управлять плеером", "<:staff:1106947414880956516>", "author"],
    ["Радио", "Режим 24/7", "<:voicechannel:1106947410246238208>", "radio"],
    ["Плеер", "Цвет плеера", "<:bluesparkles:1106953324487512186>", "cust"],
    ["Вебхук", "Настройка канала и профиля", "<:webhooks:1107006313340338236>", "wh"],
]

embed_descriptions = {
    "author": ["Права", "Добавьте роль для управления Нуар."],
    "radio": ["Режим 24/7", "Будет ли Нуар оставаться в войсе."],
    "cust": ["Плеер", "Цвет эмбеда плеера."],
    "wh": [
        "Вебхук",
        'Нуар создаст вебхук для канала выбранного канала, и вы сможете кастомизировать ее аватар и имя во вкладке "интеграции"\n**Примечание:** это работает только при наличии прав у Нуар создавать вебхуки и настроенном канале воспроизведения.',
    ],
}

for option in desc:
    options.append(
        disnake.SelectOption(
            label=option[0], description=option[1], emoji=option[2], value=option[3]
        )
    )

colorpicker = []

pick = [
    ["снежный", "⬜", "FFFAFA"],
    ["коралловый", "🟧", "FF7F50"],
    ["королевский синий", "🟦", "4169E1"],
    ["малиновый", "🟥", "DC143C"],
    ["коричневое седло", "🟫", "8B4513"],
    ["темная орхидея", "🟪", "9932CC"],
    ["лайм", "🟩", "00FF00"],
    ["золотой", "🟨", "FFD700"],
]


for color in pick:
    colorpicker.append(
        disnake.SelectOption(label=color[0], emoji=color[1], value=color[2])
    )


class MainSetup(disnake.ui.View):
    def __init__(self, node, *, timeout: float | None = 180) -> None:
        super().__init__(timeout=timeout)

        self.node = node

    @disnake.ui.string_select(
        placeholder="Что будем настраивать?", row=0, options=options
    )
    async def mainmenu(self, select, inter: disnake.Interaction):
        val = inter.data.values[0]

        embed = self.node.bot.embedding.get(
            title=embed_descriptions[val][0],
            description=embed_descriptions[val][1],
            image="https://noirplayer.su/cdn/noir%20banner%20primary.png",
        )

        # embed = genembed(
        #     title=embed_descriptions[val][0],
        #     description=embed_descriptions[val][1],
        #     image="https://noirplayer.su/cdn/noir%20banner%20primary.png",
        # )

        if val == "author":
            await inter.response.edit_message(embed=embed, view=AuthorSetup(self.node))
        elif val == "radio":
            await inter.response.edit_message(embed=embed, view=RadioSetup(self.node))
        elif val == "cust":
            await inter.response.edit_message(embed=embed, view=SliderSetup(self.node))
        elif val == "wh":
            await inter.response.send_modal(modal=WebhookSetup(self.node))


class AuthorSetup(disnake.ui.View):
    def __init__(self, node, *, timeout: float | None = 180) -> None:
        super().__init__(timeout=timeout)

        self.node = node

    @disnake.ui.role_select(placeholder="добавить роль", row=0, max_values=1)
    async def approved_roles(self, select, inter: disnake.Interaction):
        # table("guilds").update_one({"id": inter.guild_id}, {"$set": {"role" : inter.data.values[0]}}, upsert=True)
        inter.bot.db.setup.set(inter.guild_id, "role", int(inter.data.values[0]))

        player = self.node.get_player(inter.guild_id)

        if player:
            await player.refresh_init()

        await inter.response.defer(ephemeral=True)

    @disnake.ui.button(
        emoji="<:leave:1107004941333168160>",
        label="Назад",
        row=1,
        style=disnake.ButtonStyle.blurple,
    )
    async def leave(self, button, inter):
        settings = db.get_setup(inter.guild.id) or {}

        await inter.response.edit_message(
            embed=disnake.Embed(
                title="Setup Noir",
                description="**{}**\n```yaml\n# Основные\n24/7    - {}\nwebhook - {}\ncolor   - {}\nrole    - {}\n\n# Подписка\nlevel  - {}\nperiod - from {} to {}\n\n```".format(
                    inter.guild.name,
                    settings.get("24/7", "Disabled"),
                    settings.get("webhook", {}).get("name", "Disabled"),
                    settings.get("color", "Default"),
                    settings.get("role", "everyone"),
                    0,
                    "now",
                    "infinity",
                ),
                color=16711679,
            ).set_image("https://noirplayer.su/cdn/noir%20banner%20primary.png"),
            view=MainSetup(self.node),
        )

    @disnake.ui.button(label="сбросить", row=1, style=disnake.ButtonStyle.blurple)
    async def approve_everyone(self, button, inter: disnake.Interaction):
        # table("guilds").update_one({"id": inter.guild_id}, {"$unset": {"role": 1}}, upsert=True)
        inter.bot.db.setup.set(inter.guild_id, "role")

        player = self.node.get_player(inter.guild_id)

        if player:
            await player.refresh_init()

        await inter.response.defer(ephemeral=True)


class RadioSetup(disnake.ui.View):
    def __init__(self, node, *, timeout: float | None = 180) -> None:
        super().__init__(timeout=timeout)

        self.node = node

    @disnake.ui.button(
        emoji="<:leave:1107004941333168160>",
        label="Назад",
        row=0,
        style=disnake.ButtonStyle.blurple,
    )
    async def leave(self, button, inter):
        settings = db.get_setup(inter.guild.id) or {}

        await inter.response.edit_message(
            embed=disnake.Embed(
                title="Setup Noir",
                description="**{}**\n```yaml\n# Основные\n24/7    - {}\nwebhook - {}\ncolor   - {}\nrole    - {}\n\n# Подписка\nlevel  - {}\nperiod - from {} to {}\n\n```".format(
                    inter.guild.name,
                    settings.get("24/7", "Disabled"),
                    settings.get("webhook", {}).get("name", "Disabled"),
                    settings.get("color", "Default"),
                    settings.get("role", "everyone"),
                    0,
                    "now",
                    "infinity",
                ),
                color=16711679,
            ).set_image("https://noirplayer.su/cdn/noir%20banner%20primary.png"),
            view=MainSetup(self.node),
        )

    @disnake.ui.button(emoji="✖️", style=disnake.ButtonStyle.blurple)
    async def disallow(self, button, inter):
        # table("guilds").update_one({"id": inter.guild_id}, {"$unset": {"radio": 1}}, upsert=True)
        inter.bot.db.setup.set(inter.guild_id, "24/7")

        player = self.node.get_player(inter.guild_id)

        if player:
            await player.refresh_init()

        await inter.response.defer(ephemeral=True)

    @disnake.ui.button(emoji="✔️", style=disnake.ButtonStyle.blurple)
    async def allow(self, button, inter):
        # table("guilds").update_one({"id": inter.guild_id}, {"$set": {"radio": True}}, upsert=True)
        inter.bot.db.setup.set(inter.guild_id, "24/7", True)

        player = self.node.get_player(inter.guild_id)

        if player:
            await player.refresh_init()

        await inter.response.defer(ephemeral=True)


class SliderSetup(disnake.ui.View):
    def __init__(self, node, *, timeout: float | None = 180) -> None:
        super().__init__(timeout=timeout)

        self.node = node

    @disnake.ui.string_select(placeholder="Цвет плеера", row=0, options=colorpicker)
    async def approve_channel(self, select, inter: disnake.Interaction):
        # table("guilds").update_one({"id": inter.guild_id}, {"$set": {"color": inter.data.values[0]}}, upsert=True)
        inter.bot.db.setup.set(inter.guild_id, "color", inter.data.values[0])

        player = self.node.get_player(inter.guild_id)

        if player:
            await player.refresh_init()

        await inter.response.defer(ephemeral=True)

    @disnake.ui.button(
        emoji="<:leave:1107004941333168160>",
        label="Назад",
        row=1,
        style=disnake.ButtonStyle.blurple,
    )
    async def leave(self, button, inter):
        settings = db.get_setup(inter.guild.id) or {}

        await inter.response.edit_message(
            embed=disnake.Embed(
                title="Setup Noir",
                description="**{}**\n```yaml\n# Основные\n24/7    - {}\nwebhook - {}\ncolor   - {}\nrole    - {}\n\n# Подписка\nlevel  - {}\nperiod - from {} to {}\n\n```".format(
                    inter.guild.name,
                    settings.get("24/7", "Disabled"),
                    settings.get("webhook", {}).get("name", "Disabled"),
                    settings.get("color", "Default"),
                    settings.get("role", "everyone"),
                    0,
                    "now",
                    "infinity",
                ),
                color=16711679,
            ).set_image("https://noirplayer.su/cdn/noir%20banner%20primary.png"),
            view=MainSetup(self.node),
        )


class WebhookSetup(disnake.ui.Modal):
    def __init__(
        self,
        node,
        *,
        title: str = "Настройка вебхука для Нуар",
        custom_id: str = "webhook_setup",
        timeout: float = 600
    ) -> None:
        self.node = node

        components = [
            disnake.ui.TextInput(
                label="Имя вебхука",
                placeholder="Noir Player (если есть id, можно ввести любое)",
                max_length=20,
                custom_id="name",
            ),
            disnake.ui.TextInput(
                label="id уже существующего вебхука",
                placeholder="1094893876164169829",
                max_length=30,
                required=False,
                custom_id="id",
            ),
        ]

        super().__init__(
            title=title, components=components, custom_id=custom_id, timeout=timeout
        )

    async def callback(self, inter: ModalInteraction):
        await inter.response.defer(ephemeral=True)

        values = list(inter.text_values.values())

        if not values[1]:
            if inter.guild.icon:
                avatar = inter.guild.icon
            else:
                avatar = None

            webhook = await inter.channel.create_webhook(name=values[0], avatar=avatar)

            # table("guilds").update_one({"id": inter.guild_id}, {"$set": {"webhook": id}}, upsert=True)
            inter.bot.db.setup.set(
                inter.guild_id,
                "webhook",
                {"id": webhook.id, "name": webhook.name, "icon": webhook.avatar.url},
            )
        else:
            try:
                webhook = await inter.bot.fetch_webhook(values[1])
            except BaseException:
                return await inter.delete_original_response()

            # table("guilds").update_one({"id": inter.guild_id}, {"$set": {"webhook": webhook.id}}, upsert=True)
            inter.bot.db.setup.set(
                inter.guild_id,
                "webhook",
                {"id": webhook.id, "name": webhook.name, "icon": webhook.avatar.url},
            )

        player = self.node.get_player(inter.guild_id)

        if player:
            await player.refresh_init(True)

        await inter.delete_original_response()
