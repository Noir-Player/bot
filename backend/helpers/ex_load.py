from os import listdir


def cogsReload(bot):
    curr, total = 1, len(listdir("./cogs")) - 1

    for filename in listdir("./cogs"):
        if filename.endswith(".py"):
            try:  # load cog
                bot.reload_extension(f"cogs.{filename[:-3]}")
                bot.log.info(f"cog {filename} reload, {curr}/{total}")

            except Exception as error:  # something in cog wrong
                bot.log.error(f"error in cog {filename}, {curr}/{total} | {error}")

            curr += 1  # + 1 for current amount


def cogsLoad(bot):
    curr, total = 1, len(listdir("./cogs")) - 1

    for filename in listdir("./cogs"):
        if filename.endswith(".py"):
            try:  # load cog
                bot.load_extension(f"cogs.{filename[:-3]}")
                bot._log.info(f"cog {filename} load, {curr}/{total}")

            except Exception as error:  # something in cog wrong
                bot.log.error(f"error in cog {filename}, {curr}/{total} | {error}")

            curr += 1  # + 1 for current amount


def routersLoad(bot):
    curr, total = 1, len(listdir("./routers")) - 1

    for filename in listdir("./routers"):
        if filename.endswith(".py"):
            try:  # load router
                bot.load_extension(f"routers.{filename[:-3]}")
                bot._log.info(f"router {filename} checked, {curr}/{total}")

            except Exception as error:  # something in cog wrong
                bot.log.error(f"error in cog {filename}, {curr}/{total} | {error}")

            curr += 1  # + 1 for current amount
