import json

from disnake.ext import commands


class NoInVoice(commands.CommandError):
    pass


class NoInVoiceWithMe(commands.CommandError):
    pass


class TrackIsLooping(commands.CommandError):
    pass


class NoCurrent(commands.CommandError):
    pass


class InvalidSource(commands.CommandError):
    pass


class InvalidIndex(commands.CommandError):
    pass


class NoSubscribe(commands.CommandError):
    pass


errors = json.load(open("data/resources/errors.json", "r", encoding="utf-8"))
