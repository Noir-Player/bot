from quart import session, websocket, request, redirect, render_template
from clients.database import Database
from clients.redis import redis
from classes.Router import Router
from classes.Broker import Broker
from classes.Player import NoirPlayer
from classes.WebModels import AddTrackRequest

import json
import asyncio
import traceback
import pomice
import datetime


players = Router(
    "players",
    __name__,
    static_folder="static",
    template_folder="templates")


db = Database()


async def fetch_player(user) -> int | None:
        """Возвращает плеер пользователя"""
        try:
            user = players.execute(players.bot.fetch_user(user))

            for player in list(players.bot.node.players.values()):
                if player.is_connected and user:
                    if user.id in [
                            member.id for member in player.channel.members]:
                        return player.guild.id

            return None
        
        except:
            traceback.print_exc()


async def fetch_server(user) -> int | None:
    """Возвращает сервер войса пользователя"""
    try:
        user = players.execute(players.bot.fetch_user(user))

        if not user:
            return None

        for guild in user.mutual_guilds:
            user = players.execute(guild.fetch_member(user.id))

            if user.voice:
                return guild.id

        return None

    except:
        traceback.print_exc()


async def fetch_voice(user):
    """Возвращает войс пользователя"""
    try:
        user = players.execute(players.bot.fetch_user(user))

        if not user:
            return

        for guild in user.mutual_guilds:
            user = players.execute(guild.fetch_member(user.id))

            if user.voice:
                return user.voice.channel

        return None
    except Exception as e:
        traceback.print_exc()


# ---------------------------------------------------------------------------------------------------------

class Executor:
    """Executor for control ws / pubsub"""
    def __init__(self) -> None:
        self._wait_for_channel = asyncio.Event()

        self.keys = [
                "destroy",
                "disconnect",
                "move",
                "remove_filter",
                "reset_filters",
                "seek",       
                "set_pause", 
                "set_volume",
                "volume_down",
                "volume_up",  
                "refresh_init",
                "skip",   
                "prev",
            ]

        self.queue_keys = [
                "clear",
                "jump",
                "remove",
                "move"
            ]  


    def _player_execute(self, key):
        return {
                "destroy":       self.player.destroy,
                "disconnect":    self.player.disconnect,
                "move":          self.player.move_to,
                "remove_filter": self.player.remove_filter,
                "reset_filters": self.player.reset_filters,
                "seek":          self.player.seek,
                "set_pause":     self.player.set_pause,
                "set_volume":    self.player.set_volume,
                "volume_down":   self.player.volume_down,
                "volume_up":     self.player.volume_up,
                "refresh_init":  self.player.refresh_init,
                "skip":          self.player.skip,
                "prev":          self.player.prev,
            }[key]
    
    def _queue_execute(self, key):
        return {
                "clear":  self.player.queue.clear,
                "remove": self.player.queue.remove,
                "move":   self.player.queue.move,
            }[key]


    async def start(self):
        self.player: NoirPlayer = players.bot.node.get_player(await fetch_player(int(session["me"].get("id"))))

        self.user = players.execute(players.bot.fetch_user(int(session['me'].get('id'))))

        self.producer = asyncio.create_task(self._receive())
        self.consumer = asyncio.create_task(self._consume())

        self.connect = bool(self.player)

        try:
            await asyncio.gather(self.producer, self.consumer, return_exceptions=True)
            
        except BaseException:
            self.producer.cancel()
            self.consumer.cancel()
            await websocket.close(1000)


    def play_track(self, data):
        query = players.execute(players.bot.node.get_tracks(data.get("query"), requester=self.user))

        if type(query) == pomice.Playlist:
            players.execute(self.player.queue.put_list(query.tracks))

            if not self.player.current:
                players.execute(self.player.play(self.player.queue.get()))
        
        elif query:
            players.execute(self.player.queue.put(query[0]))

            if not self.player.current:
                players.execute(self.player.play(self.player.queue.get()))


    def play_playlist(self, data):
        try:
            playlist = db.playlists.get_playlist(data.get('uuid'))

            if not playlist:
                return

            items = []

            for track in playlist.get("tracks"):
                try:
                    query = players.execute(players.bot.node.get_tracks(track.get('url'), requester=self.user))[0]

                    if (
                        not self.player.current
                    ):  # чтобы не создавать задержку, играть первый найденный
                        players.execute(self.player.queue.put(query))
                        players.execute(self.player.play(self.player.queue.get()))

                    else:
                        items.append(query)
                        
                except:
                    continue

            players.execute(self.player.queue.put_list(items))
        except:
            traceback.print_exc()


    def play_recommendations(self, data):
         if self.player.current and self.player.current.track_type.value in ["spotify", "youtube"]:
            query = players.execute(players.bot.node.get_recommendations(track=self.player.current, requester=self.user, **data.get('kwargs', {})))

            players.execute(self.player.queue.put_list(query.tracks if type(query) == pomice.Playlist else query))
            



    async def _receive(self) -> None:
        """Main function for receiving msgs from socket and do some actions with player (or not)"""


        while True:
            data = json.loads(await websocket.receive())

            action = data.get('action')

            try:

                if action != 'destroy' and (not self.player or not self.connect):
                    voice = await fetch_voice(self.user.id)

                    if voice and not players.bot.node.get_player(voice.guild.id):
                        self.player = players.execute(voice.connect(cls=NoirPlayer))
                        players.execute(voice.guild.change_voice_state(channel=voice, self_deaf=True))

                        self.connect = True

                        self._wait_for_channel.set()

                        await asyncio.sleep(0.3) # Delay for init broker

                    else:
                        self.player = None
                        await websocket.send(json.dumps({"message": "Voice not found", "code": 404}))
                        continue


                if action == 'destroy':
                    players.execute(self.player.destroy())
                    break

                elif action == 'play':
                    await players.run_independent(self.play_track, data)

                elif action == 'play_playlist':
                    await players.run_independent(self.play_playlist, data)

                elif action == 'star':
                    if self.player.current:
                        db.stars.add_to_stars(int(session["me"].get("id")), self.player.current_build)

                elif action == 'get_recommendations':
                    await players.run_independent(self.play_recommendations, data)

                elif action == 'loop':
                    if self.player.queue.loop_mode == pomice.LoopMode.QUEUE:
                        players.execute(self.player.queue.set_loop_mode(pomice.LoopMode.TRACK))

                    elif self.player.queue.loop_mode == pomice.LoopMode.TRACK:
                        players.execute(self.player.queue.disable_loop())

                    else:
                        players.execute(self.player.queue.set_loop_mode(pomice.LoopMode.QUEUE))

                elif action == 'remove':
                    players.execute(self.player.queue.remove(data.get('pos') if data.get('pos') != -1 else self.player.current))

                elif action == 'shuffle':
                    players.execute(self.player.queue.shuffle())

                elif action == 'pause':
                    if self.player.current:
                        players.execute(self.player.set_pause(not self.player._paused))

                elif action == 'jump':
                    try:
                        players.execute(self.player.play(self.player.queue.jump(data.get('pos'))))
                    except:
                        pass

                elif action in self.keys:
                    players.execute(self._player_execute(action)(*data.get('args', []), **data.get('kwargs', {})))

                elif action in self.queue_keys:
                    players.execute(self._queue_execute(action)(*data.get('args', []), **data.get('kwargs', {})))
                
            except:
                traceback.print_exc()


    async def _consume(self) -> None:
        if not self.player:
            await self._wait_for_channel.wait()
        
        broker = Broker(redis, self.player.guild.id)
        
        async for message in broker.subscribe():
            if message.get('members'):

                if not int(session["me"].get("id")) in message.get('members'):
                    if self.connect:
                        self.connect = False

                        await websocket.send(json.dumps({"action": "disconnect"}))
                
                else:
                    if not self.connect:
                        self.connect = True

                        await websocket.send(json.dumps({"action": "connect"}))

                continue

            if self.connect:
                await websocket.send(json.dumps(message))




@players.websocket("/sockets/player")
async def player():
    try:
        if not session.get('me') or not db.cache.get(session["me"].get("id")):
            return await websocket.close(1000, "Unauthorized")

        ex = Executor()

        await ex.start()

    except:
        traceback.print_exc()



@players.get('/api/player/current')
async def current():
    if not session.get('me') or not db.cache.get(session["me"].get("id")):
            return await websocket.close(1000, "Unauthorized")
    
    player: NoirPlayer = players.bot.node.get_player(await fetch_player(int(session["me"].get("id"))))

    if not player:
        return json.dumps({"message": "Player not found. Connect to same voice and try again", "code": 404}), 404


    now = player.current_build if player.current else {}
    
    now['position'] = player.position
    now['volume']   = player.volume
    now['pause']    = player._paused
    now['color']    = player._color.__str__()
    now['loop']     = player.queue.loop_mode.value if player.queue.loop_mode else None

    return json.dumps(now)
    


@players.get('/api/player/queue')
async def queue():
    if not session.get('me') or not db.cache.get(session["me"].get("id")):
        return await websocket.close(1000, "Unauthorized")
    
    player: NoirPlayer = players.bot.node.get_player(await fetch_player(int(session["me"].get("id"))))

    if player:
        return json.dumps([players.bot.build.track(track.info, track.track_type.value, track.thumbnail) for track in player.queue._queue])
    
    return json.dumps({"message": "Player not found. Connect to same voice and try again", "code": 404}), 404
    
@players.patch('/api/player/suggestion')
async def suggestions():
    if not session.get('me') or not db.cache.get(session["me"].get("id")):
        return await websocket.close(1000, "Unauthorized")
    data = AddTrackRequest.model_validate(await request.get_json())

    query = players.execute(players.bot.node.get_tracks(data.query))
    

    if type(query) == pomice.Playlist:
        query = query.tracks


    return json.dumps([players.bot.build.track(track.info, track.track_type.value) for track in query][:20])

@players.route("/me/queue")
async def queue_render():
    if not session.get('me') or not db.cache.get(int(session['me'].get('id'))):
        return redirect('/oauth')

    player: NoirPlayer = players.bot.node.get_player(await fetch_player(int(session["me"].get("id"))))

    if player:
        tracks = [players.bot.build.track(track.info, track.track_type.value, track.thumbnail) for track in player.queue._queue]
    else:
        tracks = []
    
    return await render_template("main/queue.html", tracks=tracks, datetime = datetime)


def setup(bot):
    players.bot = bot
