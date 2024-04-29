from quart import render_template, session, websocket
from clients.database import Database
from classes.Router import Router

import json
import asyncio
import traceback


players = Router(
    "player",
    __name__,
    static_folder="static",
    template_folder="templates")


db = Database()

@players.websocket('/sockets/hello')
async def dews():
    print('ok')
    while True:
        await websocket.send(await websocket.receive_json())


@players.route('/me/player')
async def main():
    return await render_template('errors/403.html'), 403


async def fetch_player(user) -> int | None:
        """Возвращает плеер пользователя"""
        try:
            user = players.execute(players.bot.fetch_user(user))

            for player in list(players.bot.node.players.values()):
                if player.is_connected:
                    if user.id in [
                            member.id for member in player.channel.members]:
                        return player.guild.id
                else:
                    try:
                        players.execute(player.destroy())
                    except BaseException:
                        pass

            return None
        
        except:
            traceback.print_exc()


# ---------------------------------------------------------------------------------------------------------

async def redis_listener(user, p):

    disconnected = not bool(user.get("player"))

    if disconnected:
        return

    await p.subscribe(f'noir-{user.get("player")}')

    async for msg in p.listen():
        print(msg)

        if msg.get(
                'type') == 'message':  # Если тип - сообщение - десериализуем данные json
            data = json.loads(msg.get('data'))
        else:
            continue

        if data.get('members'):
            if not int(session['me'].get('id')) in data.get('members'):
                await websocket.send(json.dumps({"action": "disconnect"}))
                disconnected = True
            else:
                if disconnected:
                    await r.publish(f'app-{user.get("player")}', json.dumps({"type": "player", "action": "fetch_current"}))

                disconnected = False

        if disconnected:
            continue

        action = data.get('action')

        if action in [
            'destroy',
            'play',
            'put',
            'seek',
            'pause',
            'volume',
            'loop',
            'remove',
                'fetch_current']:  # Sanitizer
            await websocket.send(json.dumps(data))

# ---------------------------------------------------------------------------------------------------------


async def websocket_listener(user):

    disconnected = not bool(user.get("player"))

    if disconnected:
        await websocket.send('{"action": "not found", "value": null}')

    while True:
        data = json.loads(await websocket.receive())
        data['user'] = int(session['me'].get('id'))  # identification data

        if data.get('type') == 'connect':  # If connect to voice action
            await r.publish(f'connect', json.dumps(data))
            continue

        if disconnected:  # Check connection
            continue

        if data.get('type') == 'search':
            results = await search(data.get('query'))
            await websocket.send(json.dumps({"action": "search", "results": results}))
            continue

        if not disconnected:  # Publish action to noir
            pass


# ---------------------------------------------------------------------------------------------------------

async def state_listener(user):
    pass


@players.websocket('/sockets/player')
async def sockets_playlists():
    if not session.get('me') or not await r.keys(f'*{session["me"].get("id")}'):
        return await websocket.close(1000, "Unauthorized")
    else:

        user_data = await fetch_user(int(session['me'].get('id')))

        p = r.pubsub(ignore_subscribe_messages=True)

        producer = asyncio.create_task(redis_listener(user_data, p))
        consumer = asyncio.create_task(websocket_listener(user_data))
        finder = asyncio.create_task(state_listener(user_data))

        try:
            await asyncio.gather(producer, consumer, finder, return_exceptions=True)
        except BaseException:
            print('closed')
            await p.close()
            producer.cancel()
            consumer.cancel()


def setup(bot):
    players.bot = bot
