from quart import request, session, redirect, make_response
from requests_oauthlib import OAuth2Session
from classes.Router import Router
from clients.database import Database

import traceback

# ---------------------------------------------------------------------------------------------------------

from config import *

# ---------------------------------------------------------------------------------------------------------

oauth = Router("oauth", __name__)
db = Database()

# ---------------------------------------------------------------------------------------------------------


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)

# ---------------------------------------------------------------------------------------------------------


async def make_oauth():
    # Make session
    discord = make_session(token=session.get("oauth2_token"))

    # Set session
    session['me'] = discord.get("https://discordapp.com/api/users/@me").json()
    session['connections'] = discord.get(
        'https://discordapp.com/api/users/@me/connections').json()

    # Make response with redirect (if exist)
    resp = await make_response(await make_response(redirect(request.args.get('redirect', session.pop('temp_redirect', 'https://noirplayer.su/me')))))

    # Set servers
    servers, same, other, mutual = discord.get('https://discordapp.com/api/users/@me/guilds').json(
    ), [], [], [guild.id for guild in oauth.bot.guilds]

    if type(servers) == dict:
        return await make_response(redirect('/oauth'))


    for server in servers:
        if server.get(
                'permissions') & 8 == 8:  # Если есть разрешения администратора
            server['settings'] = db.setup.get_setup(
                int(session['me'].get('id')))
            try:
                del server['settings']['_id']
            except BaseException:
                pass

            if int(server.get('id')) in mutual:
                same.append(server)

            else:
                other.append(server)

        else:
            pass

    db.cache.set({'guilds': {'same': same, 'other': other}}, session['me'].get('id'))

    # Update user profile
    db.users.set_name(
        session['me'].get('username'), int(
            session['me'].get('id')))

    # Find user for theme
    user = db.users.get_user(int(session['me'].get('id')))

    if user and user.get('theme'):
        resp.set_cookie('theme', user.get('theme'))

    # Try to find authtorized devices
    devices = db.cache.get(int(session['me'].get('id'))).get('devices')

    # If not found
    if not devices:
        # Set one device: user_agent
        db.cache.push({'devices': request.user_agent.string},
                      int(session['me'].get('id')))
    else:
        if request.user_agent.string not in devices:
            # If current device, skip
            db.cache.push({'devices': request.user_agent.string},
                          int(session['me'].get('id')))

    return resp

# ---------------------------------------------------------------------------------------------------------


@oauth.route('/oauth')
async def auth():
    scope = request.args.get('scope', 'identify connections guilds')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(
        AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    session['temp_redirect'] = request.args.get('redirect', '/me')
    return redirect(authorization_url)


@oauth.route('/callback')
async def callback():
    if (await request.values).get('error'):
        return (await request.values)['error']

    discord = make_session(state=session.get('oauth2_state'))

    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url.replace('http', 'https'))

    session['oauth2_token'] = token

    return await make_oauth()


@oauth.route('/update')
async def update():
    try:
        return await make_oauth()
    except:
        traceback.print_exc()


@oauth.route('/logout')
async def logout():
    try:
        db.cache.clear(int(session['me'].get('id')))
        session.clear()
        return redirect("https://noirplayer.su/")
    except:
        traceback.print_exc()



def setup(bot):
    oauth.bot = bot
