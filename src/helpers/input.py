import datetime
import os
import sys

from colorama import Fore, Style

from helpers.ex_load import cogsReload
from objects.bot import NoirBot


class Readinput:
    def __init__(self, bot: NoirBot):
        self.bot = bot

    async def readinput(self):
        while True:
            read = input("")

            if read == "cogsreload":
                cogsReload(self.bot)

            elif read == "help":
                print(
                    Fore.GREEN
                    + """
    cogsreload - reload all cogs
    stop       - disconnecting bot and close session
    info       - get info from discord
    switch     - switch token
    clear      - clear cache
    reload     - reload bot
                                        """
                    + Style.RESET_ALL
                )

            elif read == "stop":
                print(Fore.YELLOW + "disconnecting..." + Style.RESET_ALL)
                exit()

            elif read == "clear":
                print(Fore.YELLOW + "clearing..." + Style.RESET_ALL)
                self.bot.clear()
                print(Fore.GREEN + "done" + Style.RESET_ALL)

            elif read == "switch":
                try:
                    await self.bot.start(
                        token=input(Fore.CYAN + "token\n" + Style.RESET_ALL + ">>>")
                    )
                except Exception as exp:
                    print(Fore.RED + f"something went wrong: " + Style.RESET_ALL)

            elif read == "info":
                print(
                    Fore.GREEN
                    + f"""
    bot name: {self.bot.user}  | id: {self.bot.user.id}
    owner:    {self.bot.owner} | id: {self.bot.owner_id}
    status:   {self.bot.status}
    limit:    {self.bot.session_start_limit.reset_time}
    ============================================
    guilds:   {len(self.bot.guilds)}
    users:    {len(self.bot.users)}
    emojis:   {len(self.bot.emojis)}
    stickers: {len(self.bot.stickers)}
    ----------------
    {datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}
                """
                    + Style.RESET_ALL
                )

            elif read == "guilds":
                list = ""
                for guild in self.bot.guilds:
                    list = f"{list}\n{guild.name} [{guild.owner.name}] - {guild.member_count}"

                print(list)

            elif str.startswith(read, "fetch"):
                read.replace("fetch ", "")

                try:
                    guild = await self.bot.fetch_guild(int(read))
                except BaseException:
                    return

                feature = ""

                for feature in guild.features:
                    feature += feature + "\n"

                print(
                    Fore.MAGENTA
                    + f"""
GUILD {guild.name} | {guild.id}
============================================
OWNER:     {guild.owner.name} | {guild.owner.id}
MEMBERS:   {guild.member_count}
CHANNELS:  {len(guild.channels)}
REGION:    {guild.region}
MFA LVL:   {guild.mfa_level}
PREM TIER: {guild.premium_tier}
ROLES:     {len(guild.roles)} | {guild.roles[0].name}
============================================
MORE FEATURES:
{feature}
                """
                    + Style.RESET_ALL
                )

            elif read == "reload":
                os.execv(sys.executable, [sys.executable] + sys.argv)

            else:
                print(
                    Fore.YELLOW
                    + "unknow command. Type 'help' for get info about commands"
                    + Style.RESET_ALL
                )
