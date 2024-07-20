config = {
    'photo_selection': {
        'ranges': [
            {
                'startDate': {'year': 2024, 'month': 3, 'day': 28},
                'endDate': {'year': 2024, 'month': 6, 'day': 21}
            },
        ]
    },
    'slideshow': {
        'delay_between_photos': 10000,  # In milliseconds
        'transition_animation_duration': 500,  # In milliseconds
        'rotate_photos': True  # Useful for when the photos are in portrait mode
    },
    'general': {
        'locale': 'es_ES.UTF-8'
    },
    'time_text': {
        'show': True,
        'start_position_X': 20,
        'start_position_Y': 100,
        'format': '%H:%M',
        'font_scale': 3,
        'font_thickness': 4,
        'font_color': (255, 255, 255)
    },
    'date_text': {
        'show': True,
        'position': 'CENTER_BELOW_TIME',  # Only one available at the moment
        'margin_top_from_time': 15,
        'format': '%d de %B',
        'font_scale': 1,
        'font_thickness': 1,
        'font_color': (255, 255, 255)
    }
}
