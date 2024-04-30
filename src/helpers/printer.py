from colorama import Fore, Style
import time
from typing import Any


class Color:
    green = Fore.GREEN
    magenta = Fore.MAGENTA
    black = Fore.BLACK
    cyan = Fore.CYAN
    blue = Fore.BLUE
    red = Fore.RED
    yellow = Fore.YELLOW
    white = Fore.WHITE


def lprint(
    msg: str, color: Color | Any = Color.green, worker: str | None = None
) -> None:
    """
    Выводит в консоль сообщение.

    Аргументы
    ---------

    msg: `str`
    Сообщение для вывода в консоль.

    color: `Color | Fore` = `Color.green`
    Цвет вывода. может быть цветом из класса или Fore.

    worker: `str | None` = `None`
    Воркер в консоли. Если нет, возвращается "MAIN".

    Пример
    ------

    ```python
    lprint("Hello from main.py!", Fore.WHITE) #[Tue, 08 Aug 2023 12:07:34 MAIN] Hello from main.py!
    ```

    """

    if not worker:
        worker = "MAIN"

    print(
        color +
        f"[{time.strftime('%a, %d %b %Y %H:%M:%S', time.gmtime())} {worker}] " +
        str(msg) +
        Style.RESET_ALL)
