import disnake
from entities.bot import NoirBot
from services.persiktunes import Node
from services.persiktunes.filters import *
from validators.player import check_player_btn_decorator

# TODO move this to a separate file

FILTERS = {
    "ChannelMix": ChannelMix(tag="mix"),
    "Distortion": Distortion(tag="dist"),
    "Karaoke": Karaoke(tag="kar"),
    "LowPass": LowPass(tag="low"),
    "Rotation": Rotation(tag="rot"),
    "Tremolo": Tremolo(tag="trem"),
    "Vibrato": Vibrato(tag="vibr"),
    "Boost": Equalizer.boost(),
    "Metal": Equalizer.metal(),
    "Piano": Equalizer.piano(),
    "VaporWave": Timescale.vaporwave(),
    "Nightcore": Timescale.nightcore(),
}


@property
def options() -> list[disnake.SelectOption]:

    descriptions = [
        "Alters stereo channels for remix-style effects 🎚️",
        "Adds gritty, distorted sound 👾",
        "Reduces or removes vocals 🎤",
        "Cuts high frequencies, keeps lows 🎧",
        "Rotates audio between stereo channels 🔄",
        "Volume pulsing effect 💫",
        "Wavy pitch modulation 🌊",
        "Increases clarity and loudness 📢",
        "EQ preset for heavy, metallic tone ⚙️",
        "EQ preset tailored for piano 🎹",
        "Slower, pitched-down retro sound ✨",
        "Faster, higher-pitched style ⭐",
    ]

    res = []

    for i in range(len(FILTERS)):
        res.append(
            disnake.SelectOption(
                label=list(FILTERS.keys())[i],
                description=descriptions[i],
                emoji="<:ev_shadow_add_primary:1239113713768861877>",
            )
        )

    return res


class EffectsView(disnake.ui.View):

    def __init__(self, node: Node):
        self.node = node
        self.bot: NoirBot = node.bot

        super().__init__(timeout=600)

    @disnake.ui.select(placeholder="Add effects 💫", options=options, max_values=7)
    @check_player_btn_decorator()
    async def effects_open(self, _, inter):
        player = self.node.get_player(inter.guild_id)

        await player.reset_filters()

        for filter in inter.data.values:
            try:
                await player.add_filter(
                    FILTERS[filter],
                )
            except BaseException:
                pass

    @disnake.ui.button(
        emoji="<:ev_shadow_minus_primary:1239113854684893194>",
        label="clear",
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

    @property
    def view(self) -> disnake.ui.View:
        return EffectsView(node=self.node)

    async def send(self, ctx: disnake.Interaction):
        "Use this function with `response.defer()` first"
        await ctx.edit_original_response(view=self.view)
