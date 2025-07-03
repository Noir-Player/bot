import disnake

from objects.bot import NoirBot
from services.persiktunes import Node
from services.persiktunes.filters import *
from validators.player import check_player_btn_decorator

filters = {
    "ChannelMix": ChannelMix(tag="mix"),
    "Distortion": Distortion(tag="dist"),
    "Karaoke": Karaoke(tag="kar"),
    "LowPass": LowPass(tag="low"),
    "Rotation": Rotation(tag="rot", rotation_hertz=1),
    "Tremolo": Tremolo(tag="trem"),
    "Vibrato": Vibrato(tag="vibr"),
    "Boost": Equalizer.boost(),
    "Metal": Equalizer.metal(),
    "Piano": Equalizer.piano(),
    "VaporWave": Timescale.vaporwave(),
    "Nightcore": Timescale.nightcore(),
}

descriptions = [
    "панорамирование звука",
    "искажение",
    "убрать голос",
    "подавление высоких частот",
    "вращение",
    "колебания громкости",
    "колебания высоты",
    "усиление бассов",
    "усиление средних частот",
    "усиление средних и высоких частот",
    "понижение скорости",
    "повышение скорости",
]

options = []

for i in range(len(filters)):
    options.append(
        disnake.SelectOption(
            label=list(filters.keys())[i],
            description=descriptions[i],
            emoji="<:ev_shadow_add_primary:1239113713768861877>",
        )
    )


class EffectsView(disnake.ui.View):

    def __init__(self, node: Node):
        self.node = node
        self.bot: NoirBot = node.bot

        super().__init__(timeout=600)

    @disnake.ui.select(placeholder="Добавить эффекты...", options=options, max_values=7)
    @check_player_btn_decorator()
    async def effects_open(self, select, inter):
        player = self.node.get_player(inter.guild_id)

        await player.reset_filters()

        for filter in inter.data.values:
            try:
                await player.add_filter(
                    filters[filter],
                )
            except BaseException:
                pass

    @disnake.ui.button(
        emoji="<:ev_shadow_minus_primary:1239113854684893194>",
        label="сбросить все эффекты",
        row=2,
        style=disnake.ButtonStyle.gray,
    )
    @check_player_btn_decorator()
    async def reset_filters(self, button, inter):
        player = self.node.get_player(inter.guild_id)
        await player.reset_filters()


class EmbedEffects:

    def __init__(self, node: Node):
        self.node = node
        self.bot: NoirBot = node.bot

    def view(self) -> disnake.ui.View:
        """Return view (buttons)"""
        return EffectsView(node=self.node)

    async def send(self, ctx: disnake.Interaction, ephemeral: bool = True):
        """Send effects"""
        await ctx.edit_original_response(view=self.view())
