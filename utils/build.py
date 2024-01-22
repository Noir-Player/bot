class Build:
    """Собирает модели в словари"""

    def __init__(self) -> None:
        pass

    def track(
        self,
        info: dict,
        track_type: str,
        thumbnail: str | None = None,
        playlist: str | None = None,
    ) -> dict:
        """Собирает словарь трека"""

        title: str = info.get("title", "Неизвестное название")
        author: str = info.get("author", "Неизвестный автор")
        url: str = info.get("uri", "")
        identifier: str = info.get("identifier", "")

        if not thumbnail:
            thumbnail: str = info.get("artworkUrl")

        # if url and track_type is TrackType.YOUTUBE:
        #     thumbnail = f"https://img.youtube.com/vi/{identifier}/default.jpg"

        length: int = info.get("length", 0)

        build = {
            "title": title,
            "author": author,
            "thumbnail": thumbnail,
            "url": url,
            "id": identifier,
            "length": length,
            "playlist": playlist,
            "type": track_type,
        }

        return build

    def playlist(
        self,
        title: str,
        thumbnail: str | None,
        description: str,
        public: bool,
        tracks: list,
        metric: dict | None,
        author: dict,
        forked: list | None,
        uuid: str,
    ) -> dict:
        """Собирает словарь плейлиста"""

        build = {
            "title": title,
            "thumbnail": thumbnail,
            "description": description,
            "public": public,
            "tracks": tracks,
            "metric": metric,
            "author": author,
            "forked": forked,
            "uuid": uuid,
        }

        return build

    def settings(
        self,
        id: int,
        radio: bool = False,
        role: int | None = None,
        color: int | None = None,
        channel: int | None = None,
        webhook: dict | None = None,
        local: str = "ru",
    ) -> dict:
        """Собирает словарь настроек OLD"""

        build = {
            "24/7": radio,
            "role": role,
            "color": color,
            "channel": channel,
            "webhook": webhook,
            "local": local,
            "id": id,
        }

        return build
