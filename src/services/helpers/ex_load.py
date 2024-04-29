import logging

from os import listdir
from utils.printer import *


def cogsReload(bot):
    curr, total = 1, len(listdir("./cogs")) - 3  # cogs - folder

    for filename in listdir("./cogs"):
        if filename.endswith(".py"):
            try:  # load cog
                bot.reload_extension(f"cogs.{filename[:-3]}")
                lprint(f"cog {filename} reload, {curr}/{total}")

            except Exception as error:  # something in cog wrong
                lprint(
                    f"error in cog {filename}, {curr}/{total} | {error}",
                    Color.red)
                logging.error(f"cog filename not load: {error}")

            curr += 1  # + 1 for current amount


def cogsLoad(bot):
    curr, total = 1, len(listdir("./cogs")) - 3  # cogs - folder

    for filename in listdir("./cogs"):
        if filename.endswith(".py"):
            # try: # load cog
            bot.load_extension(f"cogs.{filename[:-3]}")
            lprint(f"cog {filename} load, {curr}/{total}", Color.cyan)

            # except Exception as error: # something in cog wrong
            # print(Fore.YELLOW + f"error in cog {filename}, {curr}/{total} | {error}" + Style.RESET_ALL)
            # logging.error(f"cog filename not load: {error}")

            curr += 1  # + 1 for current amount


def routersLoad(bot):
    curr, total = 1, len(listdir("./routers")) - 1  # cogs - folder

    for filename in listdir("./routers"):
        if filename.endswith(".py"):
            # try: # load router
            bot.load_extension(f"routers.{filename[:-3]}")
            lprint(
                f"router {filename} checked, {curr}/{total}",
                Color.cyan,
                "ROUTER")

            # except Exception as error: # something in cog wrong
            # print(Fore.YELLOW + f"error in cog {filename}, {curr}/{total} | {error}" + Style.RESET_ALL)
            # logging.error(f"cog filename not load: {error}")

            curr += 1  # + 1 for current amount
