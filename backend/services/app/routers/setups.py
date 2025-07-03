import json

from quart import redirect, render_template, request, session, websocket

from services.database.core import Database

from ..router import Router

setups = Router("setups", __name__, static_folder="static", template_folder="templates")

db = Database()


@setups.route("/me/servers", methods=["GET", "POST"])
async def main():
    if not session.get("me") or not db.cache.get(int(session["me"].get("id"))):
        return redirect("/oauth")

    servers: dict = db.cache.get(session["me"].get("id")).get("guilds")

    # '403.html'), 403
    return await render_template("main/servers.html", servers=servers, settings=None)


# ---------------------------------------------------------------------------------------------------------


@setups.route("/me/servers/<int:server>")
async def server(server):
    if not session.get("me") or not db.cache.get(int(session["me"].get("id"))):
        return redirect("/oauth")

    servers: dict = db.cache.get(session["me"].get("id")).get("guilds")

    local = [i for i in servers.get("same") if int(i.get("id")) == server]

    if not local:
        return await render_template("errors/404.html"), 404

    return await render_template(
        "main/server.html", server=local[0], settings=db.setup.get_setup(server)
    )


# ---------------------------------------------------------------------------------------------------------


# @setups.post('/api/setup/<int:server>')
# async def setupserver(server):
#     servers: dict = json.loads(await r.get(f"guilds_{session['me'].get('id')}"))

#     if server not in [int(i.get('id')) for i in servers.get('same')]:
#         return await render_template('errors/403.html'), 403

#     form = await request.form

#     if not form:
#         return redirect('/me/servers')

#     db.setup.force_set(server, {
#             "webhook.name": form.get("hook_name"),
#             "webhook.icon": form.get("hook_icon"),
#             "color": form.get("color") if form.get("color") else None,
#             "24/7": bool(form.get("check")),
#             "role": int(form.get("role")) if form.get("role") else '',
#             "volume_step": int(form.get("volume_step")) if form.get("volume_step") else 25,
#             "disable_eq": bool(form.get("disable_eq")) if form.get("disable_eq") else False
#         })

#     table("guilds").update_one({"id": server}, {
#         "$set": {
#             "webhook.name": form.get("hook_name"),
#             "webhook.icon": form.get("hook_icon"),
#             "color": form.get("color") if form.get("color") else None,
#             "24/7": bool(form.get("check")),
#             "role": int(form.get("role")) if form.get("role") else '',
#             "volume_step": int(form.get("volume_step")) if form.get("volume_step") else 25,
#             "disable_eq": bool(form.get("disable_eq")) if form.get("disable_eq") else False
#         }
#     })

#     player = setups.bot.node.get_player(server)

#     if player:
#         await player.refresh_init(force=True)

#     # await r.publish(f'app-{server}', json.dumps({'type': 'action', 'action': 'refresh_init', 'args': {"force": True}}))

#     return redirect('/me/servers')

# ---------------------------------------------------------------------------------------------------------


# @setups.websocket('/sockets/setup')
# async def sockets_webhook():
#     if not session.get('me') or not db.cache.get(int(session['me'].get('id'))):
#         return await websocket.send(json.dumps({"status": "Unauthorized", "code": 401})), 401
#     else:

#         await websocket.accept()

#     try:
#         while True:
#             data = json.loads(await websocket.receive())

#             if data.get('action') == 'create_webhook':
#                 if not data.get('channel'):
#                     await websocket.send(json.dumps({"status": "Channel not found", "code": 404})), 404
#                     continue

#                 if await create_webhook(int(data.get('channel')), int(data.get('guild'))):
#                     await websocket.send(json.dumps({"status": "ok", "code": 200}))

#                 else:
#                     await websocket.send(json.dumps({"status": "Channel not found", "code": 404})), 404

#     except BaseException:
#         pass


def setup(bot):
    setups.bot = bot
