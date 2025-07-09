from disnake import Guild

from . import *

# TODO database clear guild


class GuildLeaveLogEmbed(ErrorEmbed):
    def __init__(self, guild: Guild):

        title = f"Leave from `{guild.name}`"

        self.add_field(
            name="Owner",
            value=guild.owner.name if guild.owner else "Unknown",
            inline=True,
        )
        self.add_field(name="Members", value=guild.member_count, inline=True)
        self.add_field(
            name="Boosts", value=guild.premium_subscription_count, inline=True
        )

        if guild.icon:
            self.set_thumbnail(url=guild.icon.url)

        self.set_footer(text=guild.id)

        super().__init__(title)


class GuildJoinLogEmbed(SuccessEmbed):
    def __init__(self, guild: Guild):

        title = f"Join on `{guild.name}`"

        self.add_field(
            name="Owner",
            value=guild.owner.name if guild.owner else "Unknown",
            inline=True,
        )
        self.add_field(name="Members", value=guild.member_count, inline=True)
        self.add_field(
            name="Boosts", value=guild.premium_subscription_count, inline=True
        )

        if guild.icon:
            self.set_thumbnail(url=guild.icon.url)

        self.set_footer(text=guild.id)

        super().__init__(title)
