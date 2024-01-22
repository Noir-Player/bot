from quart import session, request, make_response, redirect
import json, traceback, asyncio, disnake

from checks.check_auth import unauthorized_handler

from classes.WebModels import *

from classes.Router import Router

from clients.database import Database

db = Database()


apiservers = Router("apiservers", __name__, template_folder="templates", url_prefix="/api/servers")


def authorize(obj: dict):
    obj['id'] = int(session['me'].get('id'))
    return obj

def remove_none_values(d: dict):
    return {k: v for k, v in d.items() if bool(v) or v == False}


# GET

@apiservers.get('/')
async def guilds():
    await unauthorized_handler(session)

    return json.dumps(db.cache.get(int(session['me'].get('id'))).get('guilds'))

@apiservers.get('/<int:guild_id>')
async def guild(guild_id):
    await unauthorized_handler(session)

    try:
        assert guild_id in [int(guild.get('id')) for guild in db.cache.get(int(session['me'].get('id')))['guilds'].get('same')]
        
        return json.dumps(db.setup.get_setup(guild_id))

    except:
        return json.dumps({"message": "Guild not found. Please update guilds info (/update)", "code": 404}), 404

# POST

@apiservers.post('/<int:guild_id>/edit')
async def edit_guild(guild_id):
    await unauthorized_handler(session)
    try:
        data = await request.get_json()
        data['webhook']['id'] = db.setup.get_setup(guild_id).get('webhook', {}).get('id')
        data = Setup.model_validate(await request.get_json())

        try:
            assert guild_id in [int(guild.get('id')) for guild in db.cache.get(int(session['me'].get('id')))['guilds'].get('same')]
            player = apiservers.bot.node.get_player(guild_id)

            if player:
                await player.refresh_init(force=True)

            return json.dumps(db.setup.force_set(guild_id, data.model_dump()))
        
        except:
            return json.dumps({"message": "Guild not found. Please update guilds info (/update)", "code": 404}), 404
    except:
        traceback.print_exc()


@apiservers.post('/<int:guild_id>/create-webhook')
async def create_webhook(guild_id):
    await unauthorized_handler(session)

    data = CreateWebhookRequest.model_validate(await request.get_json())

    try:
        assert guild_id in [int(guild.get('id')) for guild in db.cache.get(int(session['me'].get('id')))['guilds'].get('same')]
        guild = apiservers.execute(apiservers.bot.fetch_guild(guild_id))
        channel = apiservers.execute(guild.fetch_channel(data.channel))

    except:
        return json.dumps({"message": "Guild or channel not found. Please update guilds info (/update)", "code": 404}), 404


    try:
        webhook = apiservers.execute(channel.create_webhook(
            name=data.name, avatar=guild.icon
        ))

    except Exception as e:
        return json.dumps({"status": "error", "msg": "Unknown error"}), 500

    return json.dumps(db.setup.webhook(guild_id, webhook.id, data.name))



def setup(bot):
    apiservers.bot = bot