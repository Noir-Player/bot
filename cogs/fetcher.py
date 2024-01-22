from disnake.ext import commands
from classes.Bot import NoirBot
from classes.Player import NoirPlayer
import disnake
import json
import pomice
import threading as th
import logging
import traceback

from utils.printer import *


class Fetcher(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        # self.redis = bot.redis
        self.pool = bot.pool

        # NOTE disabled in major version
        # self.bot.loop.create_task(self.startup())

    async def startup(self):
        await self.bot.wait_until_ready()

        self.fetch_voice_task = self.bot.loop.create_task(self.fetch_voice())
        self.fetch_track_task = self.bot.loop.create_task(self.fetch_track())
        self.fetch_guilds_task = self.bot.loop.create_task(self.fetch_guilds())
        self.fetch_webhook_task = self.bot.loop.create_task(
            self.fetch_webhook())
        self.connect_task = self.bot.loop.create_task(self.connect())

    # -------------------------------------------------------------------------------------------------------------------------------------
    # VOICE_STATE_UPDATE ИВЕНТ

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: disnake.Member,
        before: disnake.VoiceState,
        after: disnake.VoiceState,
    ):
        if not self.bot.pool.node_count:
            return

        player: NoirPlayer = self.bot.node.get_player(member.guild.id)

        if not player:
            return

        if not player.channel:
            try:
                return await player.destroy()
            except Exception as e:
                lprint(f"Exception", Color.red, "ERROR")
                traceback.print_exc()
                lprint(f"End of traceback", Color.red, "ERROR")
                logging.error(f"error fetcher:")
                logging.error(traceback.format_exc())
                return

        if (
            not member.guild.voice_client
            or len(player.channel.members) < 2
            and not player.is_radio
            or member == self.bot.user
            and not after.channel
        ):
            try:
                return await player.destroy()
            except BaseException:
                pass

        # if (
        #     not member.guild.voice_client.channel.id
        #     in [before.channel.id if before.channel else after.channel.id]
        #     or member.id != self.bot.user.id
        # ):
        #     return
        
        await self.bot.redis.publish(
            f'player-{member.guild.id}',
            json.dumps(
                {
                    "members": [user.id for user in player.channel.members]
                }
            )
        )

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def player(self, user) -> int | None:
        """Возвращает плеер пользователя"""
        try:
            user = await self.bot.fetch_user(user)

            for player in list(self.bot.pool.get_node().players.values()):
                if player.is_connected:
                    if user.id in [
                            member.id for member in player.channel.members]:
                        return player.guild.id
                else:
                    try:
                        await player.destroy()
                    except BaseException:
                        pass

            return None

        except Exception as e:
            lprint(f"Exception", Color.red, "ERROR")
            traceback.print_exc()
            lprint(f"End of traceback", Color.red, "ERROR")
            logging.error(f"error fetcher:")
            logging.error(traceback.format_exc())
            raise e

    async def server(self, user) -> int | None:
        """Возвращает сервер войса пользователя"""
        try:
            user = self.bot.get_user(user)

            if not user:
                return None

            for guild in user.mutual_guilds:
                user = await guild.fetch_member(user.id)

                if user.voice:
                    return guild.id

            return None

        except Exception as e:
            lprint(f"Exception", Color.red, "ERROR")
            traceback.print_exc()
            lprint(f"End of traceback", Color.red, "ERROR")
            logging.error(f"error fetcher:")
            logging.error(traceback.format_exc())
            raise e

    async def voice(self, user):
        """Возвращает войс пользователя"""
        try:
            user = self.bot.get_user(user)

            if not user:
                return

            for guild in user.mutual_guilds:
                user = await guild.fetch_member(user.id)

                if user.voice:
                    return user.voice.channel

            return None
        except Exception as e:
            lprint(f"Exception", Color.red, "ERROR")
            traceback.print_exc()
            lprint(f"End of traceback", Color.red, "ERROR")
            logging.error(f"error fetcher:")
            logging.error(traceback.format_exc())
            raise e

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def exception_handler(ex: Exception, pubsub, thread: th.Thread):
        print(ex)
        thread.stop()
        thread.join(timeout=1.0)
        pubsub.close()

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def fetch_voice(self):
        p = self.redis.pubsub()
        await p.subscribe("fetch-user")

        async for msg in p.listen():  # Прослушивание канала
            try:
                if (
                    msg.get("type") == "message"
                ):  # Если тип - сообщение - десериализуем данные json
                    data = json.loads(msg.get("data"))
                else:
                    continue

                if data.get("type") == "fetch":
                    await self.redis.publish(
                        f"fetch-user",
                        json.dumps(
                            {
                                "user": data.get("user"),
                                # "voice": await self.voice(data.get('user')),
                                # "server": await self.server(data.get('user')),
                                "player": await self.player(data.get("user")),
                            }
                        ),
                    )

            except Exception as e:
                lprint(f"Exception", Color.red, "ERROR")
                traceback.print_exc()
                lprint(f"End of traceback", Color.red, "ERROR")
                logging.error(f"error fetcher:")
                logging.error(traceback.format_exc())
                raise e

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def fetch_guilds(self) -> None:
        p = self.redis.pubsub()
        await p.subscribe("fetch-guilds")

        async for msg in p.listen():  # Прослушивание канала
            if (
                msg.get("type") == "message"
            ):  # Если тип - сообщение - десериализуем данные json
                data = json.loads(msg.get("data"))
            else:
                continue

            if data.get("type") == "autorized":
                same, other = [], []

                for guild in list(data.get("guilds")):
                    if int(guild.get("id")) in [
                            guild.id for guild in self.bot.guilds]:
                        same.append(guild)
                    else:
                        other.append(guild)

                await self.redis.set(
                    f'guilds_{data.get("user")}',
                    json.dumps({"same": same, "other": other}),
                )

                await self.redis.publish(
                    "fetch-guilds",
                    json.dumps({"user": data.get("user"), "status": "ok"}),
                )

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def fetch_track(self) -> None:
        p = self.redis.pubsub()
        await p.subscribe("fetch-track")

        async for msg in p.listen():  # Прослушивание канала
            if (
                msg.get("type") == "message"
            ):  # Если тип - сообщение - десериализуем данные json
                data = json.loads(msg.get("data"))
            else:
                continue

            if data.get("type") == "fetch":
                try:
                    query = await self.bot.node.get_tracks(data.get("track"))
                except BaseException:
                    await self.redis.publish(
                        "fetch-track",
                        json.dumps(
                            {
                                "track": None,
                                "request": data.get("track"),
                                "playlist": False,
                            }
                        ),
                    )
                    continue

                if isinstance(query, pomice.Playlist):
                    i = 0
                    for track in query.tracks:
                        await self.redis.publish(
                            f"fetch-track",
                            json.dumps(
                                {
                                    "track": self.bot.build.track(
                                        track.info,
                                        track.track_type.value,
                                        track.thumbnail,
                                    ),
                                    "request": data.get("track"),
                                    "playlist": True,
                                    "index": i,
                                    "last": query.track_count - 1,
                                }
                            ),
                        )
                        i += 1
                else:
                    track = query[0]
                    if track.is_stream:
                        return

                    await self.redis.publish(
                        "fetch-track",
                        json.dumps(
                            {
                                "track": self.bot.build.track(
                                    track.info, track.track_type.value, track.thumbnail
                                ),
                                "request": data.get("track"),
                                "playlist": False,
                            }
                        ),
                    )

            elif data.get("type") == "search":
                try:
                    query = await self.bot.node.get_tracks(
                        data.get("query"), search_type=pomice.SearchType.ytmsearch
                    )
                except BaseException:
                    await self.redis.publish(
                        f"fetch-track",
                        json.dumps({"results": [], "s_request": data.get("query")}),
                    )
                    continue

                if isinstance(query, pomice.Playlist):
                    await self.redis.publish(
                        f"fetch-track",
                        json.dumps(
                            {
                                "results": [
                                    {
                                        "type": "playlist",
                                        "title": query.name,
                                        "url": query.uri,
                                        "count": query.track_count,
                                    }
                                ],
                                "s_request": data.get("query"),
                            }
                        ),
                    )

                elif query:
                    await self.redis.publish(
                        f"fetch-track",
                        json.dumps(
                            {
                                "results": [
                                    self.bot.build.track(
                                        track.info,
                                        track.track_type.value,
                                        track.thumbnail,
                                    )
                                    for track in query
                                ],
                                "s_request": data.get("query"),
                            }
                        ),
                    )

            else:
                continue

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def fetch_webhook(self):
        p = self.redis.pubsub()
        await p.subscribe("fetch-webhook")

        async for msg in p.listen():  # Прослушивание канала
            if (
                msg.get("type") == "message"
            ):  # Если тип - сообщение - десериализуем данные json
                data = json.loads(msg.get("data"))
            else:
                continue

            if data.get("type") == "create":
                try:
                    guild = self.bot.get_guild(data.get("guild"))
                    channel = guild._channels.get(data.get("channel"))

                    if not guild or not channel:
                        await self.redis.publish(
                            "fetch-webhook",
                            json.dumps(
                                {"status": "error", "msg": "Guild or channel not found"}
                            ),
                        )
                        continue

                except Exception as e:
                    await self.redis.publish(
                        "fetch-webhook",
                        json.dumps({"status": "error", "msg": e.__str__()}),
                    )
                    continue

                if guild.icon:
                    avatar = guild.icon
                else:
                    avatar = None

                try:
                    webhook = await channel.create_webhook(
                        name=data.get("name", "Noir Player"), avatar=avatar
                    )

                except Exception as e:
                    await self.redis.publish(
                        "fetch-webhook",
                        json.dumps({"status": "error", "msg": e.__str__()}),
                    )
                    continue

                self.bot.db.table("guilds").update_one(
                    {"id": guild.id},
                    {"$set": {"webhook": {"id": webhook.id, "name": webhook.name}}},
                    upsert=True,
                )

                await self.redis.publish(
                    "fetch-webhook",
                    json.dumps(
                        {
                            "status": "ok",
                            "id": webhook.id,
                            "name": webhook.name,
                            "channel": data.get("channel"),
                        }
                    ),
                )

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def connect(self) -> None:
        p = self.redis.pubsub()
        await p.subscribe("connect")

        async for msg in p.listen():  # Прослушивание канала
            if (
                msg.get("type") == "message"
            ):  # Если тип - сообщение - десериализуем данные json
                data = json.loads(msg.get("data"))
            else:
                continue

            if data.get("type") == "connect":
                voice = await self.voice(data.get("user"))

                if voice and not self.bot.node.get_player(voice.guild.id):
                    await voice.connect(cls=NoirPlayer)
                    await voice.guild.change_voice_state(channel=voice, self_deaf=True)


def setup(bot: commands.Bot):
    bot.add_cog(Fetcher(bot))
