import disnake
from exceptions import on_view_error
from services.persiktunes import Node
from services.persiktunes.filters import *
from validators.player import check_player_btn

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
                emoji="<:filter_alt:1397155364046241924>",
            )
        )

    return res


class EffectsView(disnake.ui.View):

    def __init__(self, node: Node):
        self.node = node

        super().__init__(timeout=600)

        self.on_error = on_view_error  # type: ignore

    @disnake.ui.select(placeholder="Add effects 💫", options=options(), max_values=7)
    @check_player_btn()
    async def effects_open(self, _, inter):
        player = self.node.get_player(inter.guild_id)

        await player.reset_filters()  # type: ignore

        for filter in inter.data.values:
            try:
                await player.add_filter(  # type: ignore
                    FILTERS[filter],
                )
            except BaseException:
                pass

    @disnake.ui.button(
        emoji="<:filter_alt_off:1397155362301411370>",
        label="clear",
        row=2,
        style=disnake.ButtonStyle.gray,
    )
    @check_player_btn()
    async def reset_filters(self, button, inter):
        player = self.node.get_player(inter.guild_id)
        await player.reset_filters()  # type: ignore


class EmbedEffects:

    def __init__(self, node: Node):
        self.node = node

    @property
    def view(self) -> disnake.ui.View:
        return EffectsView(node=self.node)

    async def send(self, ctx: disnake.Interaction):
        "Use this function with `response.defer()` first"
        await ctx.edit_original_response(view=self.view)
