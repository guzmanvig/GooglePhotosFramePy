config = {
    'photo_selection': {
        'ranges': [
            {
                'startDate': {'year': 2024, 'month': 5, 'day': 28},
                'endDate': {'year': 2024, 'month': 6, 'day': 21}
            },
        ]
    },
    'slideshow': {
        'delay_between_photos': 10000,  # In milliseconds
        'transition_animation_duration': 500,  # In milliseconds
    },
    'general': {
        'locale': 'es_ES.UTF-8'
    },
    'time_text': {
        'show': True,
        'relative_position': 'BOTTOM_CENTER',  # Or TOP_CENTER
        'margin_top': 20,  # Only relevant if TOP_CENTER
        'margin_bottom': 20,  # Only relevant if BOTTOM_CENTER
        'start_position_X': 20,  # If these 2 are set, the previous ones are ignored
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
        'start_position_X': 20,  # If these 2 are set, the previous ones are ignored
        'start_position_Y': 100,
        'format': '%d de %B',
        'font_scale': 0.5,
        'font_thickness': 1,
        'font_color': (255, 255, 255)
    }
}
