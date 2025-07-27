<a name="readme-top"></a>

<div align="center">
  
  ![](https://raw.githubusercontent.com/Noir-Player/.github/refs/heads/main/Banner%20dark.png)

# Noir Player Bot

</div>

**Discord bot for listening music with a lot of features, like using such services as Spotify, Yandex Music, creating playlists directly, interacting via web interface and much more**

## Features 👾

- **A lot of sources 🎶** listen music from Spotify, Yandex Music, Apple Music, directly in discord and more

- **Discord bot UI Kit ✨** use buttons, modals and dropdowns for interacting

- **Playlists, liked music, users 📃** bot can keep in mind your favorite music and manage your own playlists

- **Web interface 💻** interacting with bot via web interface in your browser or discord activity page [WIP]

- **Localization 🈳** support for different languages [WIP]

## Installation and usage 🚀

You can use public instanse as usual bot, but if you want to run your own bot, you can clone this repository and run it yourself.

#### Requirements 📦

- `Docker`

OR

- `Python 3.12+`
- `MongoDB`
- `Lavalink` [github](https://github.com/freyacodes/Lavalink)
- `Redis` (for web [WIP])
- `Nginx` (for web [WIP])
- `NodeJS` (for web [WIP])

if You are using Docker, you can run it after creating bot in [developer portal](https://discord.com/developers/applications).

> [!IMPORTANT]
> Turn on `Presence Intent` for correct work of bot

#### Env & configs 📝

There are two files with config for setup the bot:

`.env` (`backend/.env.example`)

```env
# Bot mode: dev or prod
# MODE=dev

# Discord bot token
TOKEN=your_discord_bot_token_here

# Whether to sync commands (True or False)
# SYNC_COMMANDS=True

# Number of shards
# SHARD_COUNT=1

# Bot activity name (displayed in Discord status)
# ACTIVITY_NAME=noirplayer.su

# Activity status (check enum for options)
# ACTIVITY_STATUS=2

# Redis configuration (if not running via Docker or if using a different network)
# REDIS_HOST=localhost
# REDIS_PORT=6379

# MongoDB configuration (if not running via Docker or if using a different network)
# MONGODB_HOST=localhost
# MONGODB_PORT=27017

# Lavalink configuration (if not running via Docker or if using a different network)
# LAVALINK_HOST=localhost
# LAVALINK_PORT=2333
# LAVALINK_PASSWORD=youshallnotpass

# Logging level (in uppercase): debug, info, warning, error
# LOGLEVEL=INFO

# Spotify API credentials
# SPOTIFY_CLIENT_ID=your_spotify_client_id
# SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Support server configuration
# SUPPORT_SERVER_ID=123456789012345678
# SUPPORT_SERVER_INVITE=https://discord.gg/yourinvitecode

# Logs channel ID
# LOGS_CHANNEL_ID=123456789012345678
```

After setup `.env` you need to setup `application.yml` (`lavalink/application-example.yml`):

```yaml
plugins:
  youtube:
    enabled: true
    allowSearch: true
    allowDirectVideoIds: true
    allowDirectPlaylistIds: true
    clients:
      - MUSIC
      - ANDROID_VR
      - WEB
      - WEBEMBEDDED

  lavalyrics:
    sources:
      - spotify
      - youtube
      - yandexMusic

  lavasrc:
    providers:
      - 'ytsearch:"%ISRC%"' # Will be ignored if track does not have an ISRC. See https://en.wikipedia.org/wiki/International_Standard_Recording_Code
      - "ytsearch:%QUERY%" # Will be used if track has no ISRC or no track could be found for the ISRC
    sources:
      spotify: true # Enable Spotify source
      applemusic: ❌ # Enable Apple Music source
      deezer: ❌ # Enable Deezer source
      yandexmusic: true # Enable Yandex Music source
      flowerytts: ❌ # Enable Flowery TTS source
      youtube: true # Enable YouTube search source (https://github.com/topi314/LavaSearch)
      vkmusic: ❌ # Enable Vk Music source
      tidal: ❌ # Enable Tidal source
      qobuz: ❌ # Enabled qobuz source
      ytdlp: ❌ # Enable yt-dlp source
    lyrics-sources:
      spotify: true # Enable Spotify lyrics source
      deezer: ❌ # Enable Deezer lyrics source
      youtube: true # Enable YouTube lyrics source
      yandexmusic: true # Enable Yandex Music lyrics source
      vkmusic: ❌ # Enable Vk Music lyrics source
    spotify:
      # clientId & clientSecret are required for using spsearch
      clientId: "your client id"
      clientSecret: "your client secret"
      # spDc: "your sp dc cookie" # the sp dc cookie used for accessing the spotify lyrics api
      countryCode: "US" # the country code you want to use for filtering the artists top tracks. See https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
      playlistLoadLimit: 6 # The number of pages at 100 tracks each
      albumLoadLimit: 6 # The number of pages at 50 tracks each
      resolveArtistsInSearch: true
      localFiles: ❌
      preferAnonymousToken: ❌
    yandexmusic:
      accessToken: "your access token" # the token used for accessing the yandex music api. See https://github.com/topi314/LavaSrc#yandex-music
      playlistLoadLimit: 1 # The number of pages at 100 tracks each
      albumLoadLimit: 1 # The number of pages at 50 tracks each
      artistLoadLimit: 1 # The number of pages at 10 tracks each
    youtube:
      countryCode: "US" # the country code you want to use for searching & lyrics. See https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
      language: "en" # the language code you want to use for searching & lyrics. See https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes

lavalink:
  plugins:
    - dependency: "com.github.topi314.lavasrc:lavasrc-plugin:4.7.3"
      repository: "https://maven.lavalink.dev/releases"

    - dependency: "com.github.topi314.lavasearch:lavasearch-plugin:1.0.0"
      repository: "https://maven.lavalink.dev/releases"

    - dependency: "com.github.topi314.lavalyrics:lavalyrics-plugin:1.0.0"

    - dependency: "dev.lavalink.youtube:youtube-plugin:1.13.3"
      snapshot: ❌

  server:
    password: "youshallnotpass"
    sources:
      youtube: ❌
      bandcamp: true
      soundcloud: true
      twitch: true
      vimeo: true
      nico: true
      http: true
      local: ❌

    nonAllocatingFrameBuffer: ❌ # Setting to true reduces the number of allocations made by each player at the expense of frame rebuilding (e.g. non-instantaneous volume changes)
    bufferDurationMs: 400 # The duration of the NAS buffer. Higher values fare better against longer GC pauses. Duration <= 0 to disable JDA-NAS. Minimum of 40ms, lower values may introduce pauses.
    frameBufferDurationMs: 5000 # How many milliseconds of audio to keep buffered
    opusEncodingQuality: 10 # Opus encoder quality. Valid values range from 0 to 10, where 10 is best quality but is the most expensive on the CPU.
    resamplingQuality: LOW # Quality of resampling operations. Valid values are LOW, MEDIUM and HIGH, where HIGH uses the most CPU.
    trackStuckThresholdMs: 10000 # The threshold for how long a track can be stuck. A track is stuck if does not return any audio data.
    useSeekGhosting: true # Seek ghosting is the effect where whilst a seek is in progress, the audio buffer is read from until empty, or until seek is ready.
    youtubePlaylistLoadLimit: 6 # Number of pages at 100 each
    playerUpdateInterval: 5 # How frequently to send player updates to clients, in seconds
    youtubeSearchEnabled: true
    soundcloudSearchEnabled: true
    gc-warnings: true
```

After this you can run bot with simple command:

```bash
docker compose up -d
```

Or if you need run with MongoExpress for debugging database:

```bash
docker compose up -f docker-compose-with-express.yml
```

> [!NOTE]
> Carefully use docker compose with express, it may be dangerous for your database! Use it if you run this bot on your **local** server!

### Running without docker

1. Install third-party dependencies (look around project structure)
2. Copy `backend` folder and place `.env` directly
3. Install all requirements `python3 -m pip install -r requirements.txt`
4. Run `python3 main.py`

I do not recommended this method, it is not tested and use it if you not accessed to docker only.

## Enviroment variables 🎛️

| Name                    | Description                                                                                                  | Required | Default         |
| ----------------------- | ------------------------------------------------------------------------------------------------------------ | -------- | --------------- |
| `DISCORD_TOKEN`         | Discord bot token                                                                                            | ✅       | -               |
| `SYNC_COMMANDS`         | Whether to sync commands (True or False)                                                                     | ❌       | True            |
| `SHARD_COUNT`           | Number of shards                                                                                             | ❌       | 1               |
| `ACTIVITY_NAME`         | Bot activity name (displayed in Discord status)                                                              | ❌       | noirplayer.su   |
| `ACTIVITY_STATUS`       | Activity status (playing, listening, watching and etc. Check it on developer portal)                         | ❌       | 2               |
| `REDIS_HOST`            | Redis host                                                                                                   | ❌       | redis           |
| `REDIS_PORT`            | Redis port                                                                                                   | ❌       | 6379            |
| `MONGO_HOST`            | Mongo DB host                                                                                                | ❌       | database        |
| `MONGO_PORT`            | Mongo DB port                                                                                                | ❌       | 27017           |
| `LAVALINK_HOST`         | Lavalink host                                                                                                | ❌       | lavalink        |
| `LAVALINK_PORT`         | Lavalink port                                                                                                | ❌       | 2333            |
| `LAVALINK_PASSWORD`     | Lavalink password                                                                                            | ❌       | youshallnotpass |
| `LOG_LEVEL`             | Log level (in uppercase). Avaible any value from `logging` python module (DEBUG, INFO, WARNING, ERROR, etc.) | ❌       | INFO            |
| `SPOTIFY_CLIENT_ID`     | Spotify client ID                                                                                            | ❌       | -               |
| `SPOTIFY_CLIENT_SECRET` | Spotify client secret                                                                                        | ❌       | -               |
| `SUPPORT_SERVER_ID`     | Discord support and testing server. In this server you can use some developer commands, such as `/set` group | ❌       | -               |
| `SUPPORT_SERVER_INVITE` | Discord support and testing server invite. Using in `/help` or any fallbacks                                 | ❌       | -               |
| `LOGS_CHANNEL_ID`       | Discord channel for logs. Bot will send logs there                                                           | ❌       | -               |
