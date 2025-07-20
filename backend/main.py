"""
The main file-loader for the Noir
"""

print("loading...")

import asyncio


from _logging import get_logger
from colorama import Fore, Style
from entities.bot import get_instance as get_bot
from pyfiglet import Figlet

logo = Figlet(font="5lineoblique", width=250)

print("libs & properties imported")
print("-----------------------" + Fore.MAGENTA)
print(f'{Fore.LIGHTCYAN_EX}{logo.renderText("Noir Player")}{Style.RESET_ALL}\n')
print("-----------------------")

bot = get_bot()
logger = get_logger("main")

try:
    bot.run()

except Exception as exp:
    if exp != KeyboardInterrupt:
        logger.critical(f"Connection failed: {exp}")

    else:
        logger.info(f"^C was triggered")

finally:
    logger.info(f"Shutting down...")
    asyncio.run_coroutine_threadsafe(bot.stop(), bot.loop)
    logger.info(f"See you later!")
    exit()
