"""
### Filters module `main`

This module contains all the filters used in PersikTunes.
"""

import collections
from typing import Any, Dict, List, Optional, Tuple

from .exceptions import FilterInvalidArgument, FilterTagAlreadyInUse, FilterTagInvalid


class Filter:
    """
    The base class for all filters.
    You can use these filters if you have the latest Lavalink version
    installed. If you do not have the latest Lavalink version,
    these filters will not work.

    You must specify a tag for each filter you put on.
    This is necessary for the removal of filters.
    """

    def __init__(self, *, tag: str):
        self.payload: Optional[Dict] = None
        self.tag: str = tag
        self.preload: bool = False

    def set_preload(self) -> bool:
        """Internal method to set whether or not the filter was preloaded."""
        self.preload = True
        return self.preload


class Equalizer(Filter):
    """
    Filter which represents a 15 band equalizer.
    You can adjust the dynamic of the sound using this filter.
    i.e: Applying a bass boost filter to emphasize the bass in a song.
    The format for the levels is: List[Tuple[int, float]]
    """

    def __init__(self, *, tag: str, levels: list):
        super().__init__(tag=tag)

        self.eq = self._factory(levels)
        self.raw = levels

        self.payload = {"equalizer": self.eq}

    def _factory(self, levels: List[Tuple[Any, Any]]) -> List[Dict]:
        _dict: Dict = collections.defaultdict(int)

        _dict.update(levels)
        data = [{"band": i, "gain": _dict[i]} for i in range(15)]

        return data

    def __repr__(self) -> str:
        return (
            f"<PersikTunes.EqualizerFilter tag={self.tag} eq={self.eq} raw={self.raw}>"
        )

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Equalizer):
            return False

        return self.raw == __value.raw

    @classmethod
    def flat(cls) -> "Equalizer":
        """Equalizer preset which represents a flat EQ board,
        with all levels set to their default values.
        """

        levels = [
            (0, 0.0),
            (1, 0.0),
            (2, 0.0),
            (3, 0.0),
            (4, 0.0),
            (5, 0.0),
            (6, 0.0),
            (7, 0.0),
            (8, 0.0),
            (9, 0.0),
            (10, 0.0),
            (11, 0.0),
            (12, 0.0),
            (13, 0.0),
            (14, 0.0),
        ]
        return cls(tag="flat", levels=levels)

    @classmethod
    def boost(cls) -> "Equalizer":
        """Equalizer preset which boosts the sound of a track,
        making it sound fun and energetic by increasing the bass
        and the highs.
        """

        levels = [
            (0, -0.075),
            (1, 0.125),
            (2, 0.125),
            (3, 0.1),
            (4, 0.1),
            (5, 0.05),
            (6, 0.075),
            (7, 0.0),
            (8, 0.0),
            (9, 0.0),
            (10, 0.0),
            (11, 0.0),
            (12, 0.125),
            (13, 0.15),
            (14, 0.05),
        ]
        return cls(tag="boost", levels=levels)

    @classmethod
    def metal(cls) -> "Equalizer":
        """Equalizer preset which increases the mids of a track,
        preferably one of the metal genre, to make it sound
        more full and concert-like.
        """

        levels = [
            (0, 0.0),
            (1, 0.1),
            (2, 0.1),
            (3, 0.15),
            (4, 0.13),
            (5, 0.1),
            (6, 0.0),
            (7, 0.125),
            (8, 0.175),
            (9, 0.175),
            (10, 0.125),
            (11, 0.125),
            (12, 0.1),
            (13, 0.075),
            (14, 0.0),
        ]

        return cls(tag="metal", levels=levels)

    @classmethod
    def piano(cls) -> "Equalizer":
        """Equalizer preset which increases the mids and highs
        of a track, preferably a piano based one, to make it
        stand out.
        """

        levels = [
            (0, -0.25),
            (1, -0.25),
            (2, -0.125),
            (3, 0.0),
            (4, 0.25),
            (5, 0.25),
            (6, 0.0),
            (7, -0.25),
            (8, -0.25),
            (9, 0.0),
            (10, 0.0),
            (11, 0.5),
            (12, 0.25),
            (13, -0.025),
        ]
        return cls(tag="piano", levels=levels)


class Timescale(Filter):
    """Filter which changes the speed and pitch of a track.
    You can make some very nice effects with this filter,
    i.e: a vaporwave-esque filter which slows the track down
    a certain amount to produce said effect.
    """

    def __init__(
        self, *, tag: str, speed: float = 1.0, pitch: float = 1.0, rate: float = 1.0
    ):
        super().__init__(tag=tag)

        if speed < 0:
            raise FilterInvalidArgument("Timescale speed must be more than 0.")
        if pitch < 0:
            raise FilterInvalidArgument("Timescale pitch must be more than 0.")
        if rate < 0:
            raise FilterInvalidArgument("Timescale rate must be more than 0.")

        self.speed: float = speed
        self.pitch: float = pitch
        self.rate: float = rate

        self.payload = {
            "timescale": {"speed": self.speed, "pitch": self.pitch, "rate": self.rate},
        }

    @classmethod
    def vaporwave(cls) -> "Timescale":
        """Timescale preset which slows down the currently playing track,
        giving it the effect of a half-speed record/casette playing.

        This preset will assign the tag 'vaporwave'.
        """

        return cls(tag="vaporwave", speed=0.8, pitch=0.8)

    @classmethod
    def nightcore(cls) -> "Timescale":
        """Timescale preset which speeds up the currently playing track,
        which matches up to nightcore, a genre of sped-up music

        This preset will assign the tag 'nightcore'.
        """

        return cls(tag="nightcore", speed=1.25, pitch=1.3)

    def __repr__(self) -> str:
        return f"<PersikTunes.TimescaleFilter tag={self.tag} speed={self.speed} pitch={self.pitch} rate={self.rate}>"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Timescale):
            return False

        return (
            self.speed == __value.speed
            and self.pitch == __value.pitch
            and self.rate == __value.rate
        )


class Karaoke(Filter):
    """Filter which filters the vocal track from any song and leaves the instrumental.
    Best for karaoke as the filter implies.
    """

    def __init__(
        self,
        *,
        tag: str,
        level: float = 1.0,
        mono_level: float = 1.0,
        filter_band: float = 220.0,
        filter_width: float = 100.0,
    ):
        super().__init__(tag=tag)

        self.level: float = level
        self.mono_level: float = mono_level
        self.filter_band: float = filter_band
        self.filter_width: float = filter_width

        self.payload = {
            "karaoke": {
                "level": self.level,
                "monoLevel": self.mono_level,
                "filterBand": self.filter_band,
                "filterWidth": self.filter_width,
            },
        }

    def __repr__(self) -> str:
        return (
            f"<PersikTunes.KaraokeFilter tag={self.tag} level={self.level} mono_level={self.mono_level} "
            f"filter_band={self.filter_band} filter_width={self.filter_width}>"
        )

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Karaoke):
            return False

        return (
            self.level == __value.level
            and self.mono_level == __value.mono_level
            and self.filter_band == __value.filter_band
            and self.filter_width == __value.filter_width
        )


class Tremolo(Filter):
    """Filter which produces a wavering tone in the music,
    causing it to sound like the music is changing in volume rapidly.
    """

    def __init__(self, *, tag: str, frequency: float = 2.0, depth: float = 0.5):
        super().__init__(tag=tag)

        if frequency < 0:
            raise FilterInvalidArgument(
                "Tremolo frequency must be more than 0.",
            )
        if depth < 0 or depth > 1:
            raise FilterInvalidArgument(
                "Tremolo depth must be between 0 and 1.",
            )

        self.frequency: float = frequency
        self.depth: float = depth

        self.payload = {
            "tremolo": {
                "frequency": self.frequency,
                "depth": self.depth,
            },
        }

    def __repr__(self) -> str:
        return f"<PersikTunes.TremoloFilter tag={self.tag} frequency={self.frequency} depth={self.depth}>"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Tremolo):
            return False

        return self.frequency == __value.frequency and self.depth == __value.depth


class Vibrato(Filter):
    """Filter which produces a wavering tone in the music, similar to the Tremolo filter,
    but changes in pitch rather than volume.
    """

    def __init__(self, *, tag: str, frequency: float = 2.0, depth: float = 0.5):
        super().__init__(tag=tag)

        if frequency < 0 or frequency > 14:
            raise FilterInvalidArgument(
                "Vibrato frequency must be between 0 and 14.",
            )
        if depth < 0 or depth > 1:
            raise FilterInvalidArgument(
                "Vibrato depth must be between 0 and 1.",
            )

        self.frequency: float = frequency
        self.depth: float = depth

        self.payload = {
            "vibrato": {
                "frequency": self.frequency,
                "depth": self.depth,
            },
        }

    def __repr__(self) -> str:
        return f"<PersikTunes.VibratoFilter tag={self.tag} frequency={self.frequency} depth={self.depth}>"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Vibrato):
            return False

        return self.frequency == __value.frequency and self.depth == __value.depth


class Rotation(Filter):
    """Filter which produces a stereo-like panning effect, which sounds like
    the audio is being rotated around the listener's head
    """

    def __init__(self, *, tag: str, rotation_hertz: float = 5):
        super().__init__(tag=tag)

        self.rotation_hertz: float = rotation_hertz
        self.payload = {"rotation": {"rotationHz": self.rotation_hertz}}

    def __repr__(self) -> str:
        return f"<PersikTunes.RotationFilter tag={self.tag} rotation_hertz={self.rotation_hertz}>"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Rotation):
            return False

        return self.rotation_hertz == __value.rotation_hertz


class ChannelMix(Filter):
    """Filter which manually adjusts the panning of the audio, which can make
    for some cool effects when done correctly.
    """

    def __init__(
        self,
        *,
        tag: str,
        left_to_left: float = 1,
        right_to_right: float = 1,
        left_to_right: float = 0,
        right_to_left: float = 0,
    ):
        super().__init__(tag=tag)

        if 0 > left_to_left > 1:
            raise ValueError(
                "'left_to_left' value must be more than or equal to 0 or less than or equal to 1.",
            )
        if 0 > right_to_right > 1:
            raise ValueError(
                "'right_to_right' value must be more than or equal to 0 or less than or equal to 1.",
            )
        if 0 > left_to_right > 1:
            raise ValueError(
                "'left_to_right' value must be more than or equal to 0 or less than or equal to 1.",
            )
        if 0 > right_to_left > 1:
            raise ValueError(
                "'right_to_left' value must be more than or equal to 0 or less than or equal to 1.",
            )

        self.left_to_left: float = left_to_left
        self.left_to_right: float = left_to_right
        self.right_to_left: float = right_to_left
        self.right_to_right: float = right_to_right

        self.payload = {
            "channelMix": {
                "leftToLeft": self.left_to_left,
                "leftToRight": self.left_to_right,
                "rightToLeft": self.right_to_left,
                "rightToRight": self.right_to_right,
            },
        }

    def __repr__(self) -> str:
        return (
            f"<PersikTunes.ChannelMix tag={self.tag} left_to_left={self.left_to_left} left_to_right={self.left_to_right} "
            f"right_to_left={self.right_to_left} right_to_right={self.right_to_right}>"
        )

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ChannelMix):
            return False

        return (
            self.left_to_left == __value.left_to_left
            and self.left_to_right == __value.left_to_right
            and self.right_to_left == __value.right_to_left
            and self.right_to_right == __value.right_to_right
        )


class Distortion(Filter):
    """Filter which generates a distortion effect. Useful for certain filter implementations where
    distortion is needed.
    """

    def __init__(
        self,
        *,
        tag: str,
        sin_offset: float = 0,
        sin_scale: float = 1,
        cos_offset: float = 0,
        cos_scale: float = 1,
        tan_offset: float = 0,
        tan_scale: float = 1,
        offset: float = 0,
        scale: float = 1,
    ):
        super().__init__(tag=tag)

        self.sin_offset: float = sin_offset
        self.sin_scale: float = sin_scale
        self.cos_offset: float = cos_offset
        self.cos_scale: float = cos_scale
        self.tan_offset: float = tan_offset
        self.tan_scale: float = tan_scale
        self.offset: float = offset
        self.scale: float = scale

        self.payload = {
            "distortion": {
                "sinOffset": self.sin_offset,
                "sinScale": self.sin_scale,
                "cosOffset": self.cos_offset,
                "cosScale": self.cos_scale,
                "tanOffset": self.tan_offset,
                "tanScale": self.tan_scale,
                "offset": self.offset,
                "scale": self.scale,
            },
        }

    def __repr__(self) -> str:
        return (
            f"<PersikTunes.Distortion tag={self.tag} sin_offset={self.sin_offset} sin_scale={self.sin_scale}> "
            f"cos_offset={self.cos_offset} cos_scale={self.cos_scale} tan_offset={self.tan_offset} "
            f"tan_scale={self.tan_scale} offset={self.offset} scale={self.scale}"
        )

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Distortion):
            return False

        return (
            self.sin_offset == __value.sin_offset
            and self.sin_scale == __value.sin_scale
            and self.cos_offset == __value.cos_offset
            and self.cos_scale == __value.cos_scale
            and self.tan_offset == __value.tan_offset
            and self.tan_scale == __value.tan_scale
            and self.offset == __value.offset
            and self.scale == __value.scale
        )


class LowPass(Filter):
    """Filter which supresses higher frequencies and allows lower frequencies to pass.
    You can also do this with the Equalizer filter, but this is an easier way to do it.
    """

    def __init__(self, *, tag: str, smoothing: float = 20):
        super().__init__(tag=tag)

        self.smoothing: float = smoothing
        self.payload = {"lowPass": {"smoothing": self.smoothing}}

    def __repr__(self) -> str:
        return f"<PersikTunes.LowPass tag={self.tag} smoothing={self.smoothing}>"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, LowPass):
            return False

        return self.smoothing == __value.smoothing


class Filters:
    """Helper class for filters"""

    def __init__(self) -> None:
        self._filters: List[Filter] = []

    @property
    def has_preload(self) -> bool:
        """Property which checks if any applied filters were preloaded"""
        return any(f for f in self._filters if f.preload)

    @property
    def has_global(self) -> bool:
        """Property which checks if any applied filters are global"""
        return any(f for f in self._filters if f.preload == False)

    @property
    def empty(self) -> bool:
        """Property which checks if the filter list is empty"""
        return len(self._filters) == 0

    def add_filter(self, *, filter: Filter) -> None:
        """Adds a filter to the list of filters applied"""
        if any(f for f in self._filters if f.tag == filter.tag):
            raise FilterTagAlreadyInUse(
                "A filter with that tag is already in use.",
            )
        self._filters.append(filter)

    def remove_filter(self, *, filter_tag: str) -> None:
        """Removes a filter from the list of filters applied using its filter tag"""
        if not any(f for f in self._filters if f.tag == filter_tag):
            raise FilterTagInvalid("A filter with that tag was not found.")

        for index, filter in enumerate(self._filters):
            if filter.tag == filter_tag:
                del self._filters[index]

    def edit_filter(self, *, filter_tag: str, to_apply: Filter) -> None:
        """Edits a filter in the list of filters applied using its filter tag and replaces it with the new filter."""
        if not any(f for f in self._filters if f.tag == filter_tag):
            raise FilterTagInvalid("A filter with that tag was not found.")

        for index, filter in enumerate(self._filters):
            if filter.tag == filter_tag:
                if not isinstance(filter, type(to_apply)):
                    raise FilterInvalidArgument(
                        "Edited filter is not the same type as the current filter.",
                    )
                if self._filters[index] == to_apply:
                    raise FilterInvalidArgument(
                        "Edited filter is the same as the current filter."
                    )

                if to_apply.tag != filter_tag:
                    raise FilterInvalidArgument(
                        "Edited filter tag is not the same as the current filter tag.",
                    )

                self._filters[index] = to_apply

    def has_filter(self, *, filter_tag: str) -> bool:
        """Checks if a filter exists in the list of filters using its filter tag"""
        return any(f for f in self._filters if f.tag == filter_tag)

    def has_filter_type(self, *, filter_type: Filter) -> bool:
        """Checks if any filters applied match the specified filter type."""
        return any(f for f in self._filters if isinstance(f, type(filter_type)))

    def reset_filters(self) -> None:
        """Removes all filters from the list"""
        self._filters = []

    def get_preload_filters(self) -> List[Filter]:
        """Get all preloaded filters"""
        return [f for f in self._filters if f.preload]

    def get_all_payloads(self) -> Dict[str, Any]:
        """Returns a formatted dict of all the filter payloads"""
        payload: Dict[str, Any] = {}
        for _filter in self._filters:
            if _filter.payload:
                payload.update(_filter.payload)
        return payload

    def get_filters(self) -> List[Filter]:
        """Returns the current list of applied filters"""
        return self._filters
