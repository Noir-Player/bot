from classes.ApiRouter import NOIRouter

router = NOIRouter(tags=["Main"])


@router.get("/status")
async def get_status():
    """Get status of bot (guilds, players, ...)"""
    return {
        "guilds": len(router.bot.guilds),
        "players": router.bot.node.player_count,
        "uptime": router.bot.node.stats.uptime,
        "ping": round(router.bot.latency, 3)
    }
