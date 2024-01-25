"""
The main file-loader for the Noir

supports:
- async input in terminal
- change status
- reload cogs without reload
- logging
- detection events:
  - resume
  - disconnect
  - connect
  - wrong token
  - stopped

Created by Persifox
"""


from classes.Bot import NoirBot
from pyfiglet import Figlet
from utils.printer import *
from colorama import Fore, Style
import threading
import traceback
import asyncio
import pomice
import disnake
print("loading...")


# import sdc_api_py


logo = Figlet(font="5lineoblique", width=250)

lprint("libs & properties imported")
print("-----------------------")
print(f"Powered on {disnake.__name__} | version {disnake.__version__}")
print(f"Music by   {pomice.__name__}  | version {pomice.__version__}")
print("-----------------------" + Fore.MAGENTA)
print(f'{Fore.LIGHTCYAN_EX}{logo.renderText("Noir Player")}{Style.RESET_ALL}\n')
print("-----------------------")

bot = NoirBot(debug=True)

try:
    threading.Thread(target=bot.run, name="bot").start()
    bot.serve_api()

except Exception as exp:
    if exp != KeyboardInterrupt:
        lprint(f"Connection failed: {exp}", Color.red)
        traceback.print_exc()

    else:
        lprint(f"^C was triggered", Color.yellow)

finally:
    lprint(f"Shutting down...", Color.blue)
    asyncio.run_coroutine_threadsafe(bot.stop(), bot.loop)
    lprint(f"See you later!", Color.magenta)
    exit()
