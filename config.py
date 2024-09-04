config = {
    'photo_selection': {
        'ranges': [
            {
                'startDate': {'year': 2024, 'month': 3, 'day': 28},
                'endDate': {'year': 2024, 'month': 6, 'day': 21}
            },
        ],
        'albums': ['Barcelona', 'Washington DC', 'Graduation', 'NYC 2021'],
        'shared_albums': ['ALL']  # ALL is a wildcard for all albums
    },
    'slideshow': {
        'delay_between_photos': 600000,  # In milliseconds
        'transition_animation_duration': 500,  # In milliseconds
        'display_width': 0,  # These 2 can be left as 0. Specify them only if you don't get fullscreen (happens in some devices).
        'display_height': 0,
        'pause': {
            'start': '00:00',  # If set, the slideshow will pause at this time and will show a black screen. In windows it also lowers the brightness to 0.
            'end': '09:00'
        },
        'low_brightness': {
            'start': '20:15',  # If set, the screen will dim at this time. Only for Windows
            'end': '09:00',
            'brightness': 30  # From 0 to 100
        }
    },
    'general': {
        'locale': 'es_ES.UTF-8',  # For English use en_US.UTF-8
        'refresh_photos': False,  # If True, the script will fetch new photos from Google Photos instead of using the onces in file
        'zoom_to_fit': False  # If True, the images will be zoomed and then cropped to fit the screen dimensions. If False, black margins are added to the image to fit the dimensions.
    },
    'time_text': {
        'show': True,
        'relative_position': 'BOTTOM_CENTER',  # Or TOP_CENTER
        'margin_top': 30,  # Only relevant if TOP_CENTER
        'margin_bottom': 25,  # Only relevant if BOTTOM_CENTER
        'start_position_X': 20,  # These 2 are only used if relative_position is empty
        'start_position_Y': 100,
        'format': '%H:%M',
        'font_scale': 2,
        'font_thickness': 2,
        'font_color': (255, 255, 255)
    },
    'date_text': {
        'show': True,
        'relative_position': 'CENTER_ABOVE_TIME',  # Or CENTER_BELOW_TIME
        'spacing_from_time': 15,
        'start_position_X': 20,  # These 2 are only used if relative_position is empty
        'start_position_Y': 100,
        'format': '%d de %B',
        'font_scale': 0.5,
        'font_thickness': 1,
        'font_color': (255, 255, 255)
    }
}
