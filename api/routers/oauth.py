from requests_oauthlib import OAuth2Session

import uuid

# ---------------------------------------------------------------------------------------------------------

from config import *
from api.routers.helpers.session_verify import *

from utils.printer import *

# ---------------------------------------------------------------------------------------------------------

from classes.ApiRouter import NOIRouter
from fastapi import Response, Depends, Request, Cookie
from fastapi.responses import RedirectResponse

router = NOIRouter(tags=["Oauth"])

# ---------------------------------------------------------------------------------------------------------

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
        token_updater=None)

# ---------------------------------------------------------------------------------------------------------

async def make_oauth(sessiontoken: str):
    # Make oauth
    discord = make_session(token=router.db.sessions.get_oauth_token(sessiontoken))

    # Set session
    session = router.db.sessions.set(
        {
            "user": discord.get("https://discordapp.com/api/users/@me").json(),
            "connections": discord.get('https://discordapp.com/api/users/@me/connections').json(),
        },
        token = sessiontoken
    )

    # Make response with redirect (if exist)
    resp = RedirectResponse("/discovery")

    # Set servers
    servers, same, other, mutual = discord.get('https://discordapp.com/api/users/@me/guilds').json(
    ), [], [], [guild.id for guild in router.bot.guilds]

    if type(servers) == dict:
        return RedirectResponse("/login")


    for server in servers:
        if server.get(
                'permissions') & 8 == 8:  # Если есть разрешения администратора
            server['settings'] = router.db.setup.get_setup(
                int(session["user"].get("id")))
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

    router.db.cache.set({'guilds': {'same': same, 'other': other}}, session["user"].get("id"))

    # Update user profile
    router.db.users.set_name(session["user"].get("username"),  int(session["user"].get("id")))

    # Find user for theme

    # # Try to find authtorized devices
    # devices = router.db.cache.get(int(session['me'].get('id'))).get('devices')

    # # If not found
    # if not devices:
    #     # Set one device: user_agent
    #     router.db.cache.push({'devices': resp.user_agent.string},
    #                   int(session['me'].get('id')))
    # else:
    #     if request.user_agent.string not in devices:
    #         # If current device, skip
    #         db.cache.push({'devices': request.user_agent.string},
    #                       int(session['me'].get('id')))

    return resp

@router.get("/login")
async def login(response: Response):

    key = uuid.uuid4()

    sessid = uuid.uuid5(uuid.NAMESPACE_X500, f'{key}{router.salt}')

    lprint(f'{sessid} - {key}')

    scope = 'identify connections guilds'

    discord = make_session(scope=scope.split(' '))

    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    router.db.sessions.set_oauth_state(sessid, SessionData(oauth2_state=state))

    response.set_cookie("sessionid", str(key), secure=True, httponly=True)

    return RedirectResponse(authorization_url)


@router.get('/callback', dependencies=[Depends(cookie)])
async def callback(request: Request, sessionid: str = Cookie()):

    if not sessionid:
        return {"msg": "session not passed"}, 403

    discord = make_session(state=router.db.sessions.get_oauth_state(sessionid))

    router.db.sessions.set_oauth_token(
        discord.fetch_token(
            TOKEN_URL,
            client_secret=OAUTH2_CLIENT_SECRET,
            authorization_response=request.url
        )
    )

    return await make_oauth(sessionid)

@router.get("/logout")
async def logout(response: Response, sessionid: str = Cookie()):
    router.db.sessions.clear(sessionid)
    cookie.delete_from_response(response)
    return RedirectResponse("/")

