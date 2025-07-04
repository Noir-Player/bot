"""
The main file-loader for the Noir
"""

print("loading...")

import asyncio
import threading

import disnake
from colorama import Fore, Style
from objects.bot import NoirBot
from pyfiglet import Figlet

logo = Figlet(font="5lineoblique", width=250)

print("libs & properties imported")
print("-----------------------")
print(f"Powered on {disnake.__name__} | version {disnake.__version__}")
# print(f"Music by   {.__name__}  | version {pomice.__version__}")
print("-----------------------" + Fore.MAGENTA)
print(f'{Fore.LIGHTCYAN_EX}{logo.renderText("Noir Player")}{Style.RESET_ALL}\n')
print("-----------------------")

bot = NoirBot(debug=True)

try:
    bot.run()
    # bot.serve_app() # deprecated

except Exception as exp:
    if exp != KeyboardInterrupt:
        bot._log.critical(f"Connection failed: {exp}")

    else:
        bot._log.info(f"^C was triggered")

finally:
    bot._log.info(f"Shutting down...")
    asyncio.run_coroutine_threadsafe(bot.stop(), bot.loop)
    bot._log.info(f"See you later!")
    exit()
