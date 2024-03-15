from requests_oauthlib import OAuth2Session

import uuid

# ---------------------------------------------------------------------------------------------------------

from config import *

# ---------------------------------------------------------------------------------------------------------

from classes.ApiRouter import NOIRouter
from fastapi import Request, Cookie
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

# ---------------------------------------------------------------------------------------------------------


async def make_oauth(sessiontoken: str):
    # Make oauth
    discord = make_session(
        token=(await router.session.get(sessiontoken)).get("oauth_token"))

    # Set session
    session = {
        "user": discord.get("https://discordapp.com/api/users/@me").json(),
        "connections": discord.get('https://discordapp.com/api/users/@me/connections').json(),
    }

    await router.session.set(sessiontoken, session)

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
    router.db.users.add_user(session['user'])

    return resp


@router.get("/login", description="Url для входа", status_code=307)
async def login(request: Request):

    discord = make_session(scope=SCOPES.split(' '))

    key = request.cookies.get("sessionid") or uuid.uuid4().__str__()

    authorization_url, state = discord.authorization_url(
        AUTHORIZATION_BASE_URL)
    await router.session.set(
        key,
        {"oauth_state": state}, 
        3600
        )

    response = RedirectResponse(authorization_url)

    response.set_cookie(key="sessionid", value=str(key), httponly=True, secure=True)

    return response


@router.get('/callback', description="Редирект после входа", status_code=307)
async def callback(request: Request, sessionid: str = Cookie()):
    if not sessionid:
        return {"msg": "session not passed"}

    discord = make_session(state=(await router.session.get(sessionid)).get("oauth_state"))

    await router.session.set(
        sessionid,
        {"oauth_token": discord.fetch_token(
            TOKEN_URL,
            client_secret=OAUTH2_CLIENT_SECRET,
            authorization_response=request.url.__str__().replace(
                "http://",
                "https://"))})

    return await make_oauth(sessionid)


@router.get("/logout", description="Выйти из аккаунта", status_code=307)
async def logout(sessionid: str = Cookie()):
    if not sessionid:
        return {"msg": "session not passed"}

    await router.session.delete(sessionid)

    response = RedirectResponse("/")
    response.delete_cookie("sessionid")

    return response

# @router.get("/session", description="Получить свою сессию")
# async def get_session(response: Response, sessionid: str = Cookie()):
#     if not sessionid:
#         return {"msg": "session not passed"}

#     return json.dumps(await router.session.get(sessionid))
