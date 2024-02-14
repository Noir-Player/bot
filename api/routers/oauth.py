from requests_oauthlib import OAuth2Session

import uuid

# ---------------------------------------------------------------------------------------------------------

from config import *

# ---------------------------------------------------------------------------------------------------------

from classes.ApiRouter import NOIRouter
from fastapi import Response, Request, Cookie
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
        # auto_refresh_url=TOKEN_URL,
        token_updater=None)


def get_session_keys(cookies=None):

    key = cookies.get("sessionid") or uuid.uuid4().__str__()

    return uuid.uuid5(uuid.NAMESPACE_X500,
                      f'{key}{router.salt}').__str__(), key

# ---------------------------------------------------------------------------------------------------------


async def make_oauth(sessiontoken: str):
    # Make oauth
    discord = make_session(
        token=router.db.sessions.get_oauth_token(sessiontoken))

    # Set session
    session = {
        "user": discord.get("https://discordapp.com/api/users/@me").json(),
        "connections": discord.get('https://discordapp.com/api/users/@me/connections').json(),
    }

    router.db.sessions.set(session, token=sessiontoken)

    # Make response with redirect (if exist)
    resp = RedirectResponse("/discovery")

    # Set servers
    servers, same, other, mutual = discord.get('https://discordapp.com/api/users/@me/guilds').json(
    ), [], [], [guild.id for guild in router.bot.guilds]

    if isinstance(servers, dict):  # must be array
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

    router.db.cache.set(
        {'guilds': {'same': same, 'other': other}}, session["user"].get("id"))

    # Update user profile
    router.db.users.set_name(
        session["user"].get("username"), int(
            session["user"].get("id")))

    return resp


@router.get("/login", description="Url для входа")
async def login(request: Request):

    sessid, key = get_session_keys(request.cookies)

    discord = make_session(scope=SCOPES.split(' '))

    authorization_url, state = discord.authorization_url(
        AUTHORIZATION_BASE_URL)
    router.db.sessions.set_oauth_state(
        state, sessid or request.cookies.get("sessionid"))

    response = RedirectResponse(authorization_url)

    response.set_cookie(key="sessionid", value=str(key), httponly=True, secure=True)

    return response


@router.get('/callback', description="Редирект после входа")
async def callback(request: Request, sessionid: str = Cookie()):
    if not sessionid:
        return {"msg": "session not passed"}

    discord = make_session(state=router.db.sessions.get_oauth_state(sessionid))

    router.db.sessions.set_oauth_token(
        discord.fetch_token(
            TOKEN_URL,
            client_secret=OAUTH2_CLIENT_SECRET,
            authorization_response=request.url.__str__().replace(
                "http://",
                "https://")),
        sessionid)

    return await make_oauth(sessionid)


@router.get("/logout", description="Выйти из аккаунта")
async def logout(response: Response, sessionid: str = Cookie()):
    if not sessionid:
        return {"msg": "session not passed"}

    router.db.sessions.col().delete_many({})
    router.db.sessions.clear(sessionid)
    response.delete_cookie("sessionid")
    return RedirectResponse("/")
