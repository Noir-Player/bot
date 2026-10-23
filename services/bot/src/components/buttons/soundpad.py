from assets.emojis import *
from disnake.ui import Button

SOUNDPAD_BUTTONS = (
    Button(emoji=LOOP, custom_id="loop_button_callback"),
    Button(emoji=PREVIOUS, custom_id="previous_button_callback"),
    Button(emoji=PLAYPAUSE, custom_id="play_pause_button_callback"),
    Button(emoji=NEXT, custom_id="next_button_callback"),
    Button(emoji=ACTION, custom_id="more_menu_button_callback"),
)

LIKE_BUTTON = Button(emoji=PLUS_CIRCLE, custom_id="add_to_star_button_callback")

START_AUTOPLAY_BUTTON = Button(
    emoji=AUTOPLAY, custom_id="start_autoplay_button_callback"
)
