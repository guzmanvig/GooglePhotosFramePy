import asyncio
import datetime
import os
import locale
import platform
import subprocess
import time
import traceback

import cv2
import numpy as np
from google_api import download_random_photos
from config import config
from server import start_server

locale.setlocale(locale.LC_TIME, config['general']['locale'])


def get_fullscreen_image(image_path, window_name):
    img = cv2.imread(image_path)

    # Get the dimensions of the image and the screen
    img_height, img_width = img.shape[:2]
    if config['slideshow']['display_width'] and config['slideshow']['display_height']:
        screen_width = config['slideshow']['display_width']
        screen_height = config['slideshow']['display_height']
    else:
        # Get it from the fullscreen window
        screen_width, screen_height = cv2.getWindowImageRect(window_name)[2:4]

    # Calculate aspect ratios
    img_aspect_ratio = img_width / img_height
    screen_aspect_ratio = screen_width / screen_height

    if config['general']['zoom_to_fit']:
        # Calculate scaling factors for zooming
        if screen_aspect_ratio > img_aspect_ratio:
            # Screen is wider than image, scale based on width (zoom in on height)
            scale = screen_width / img_width
            new_height = int(screen_height / scale)
            crop_y = (img_height - new_height) // 2
            cropped_img = img[crop_y:crop_y + new_height, :]
            result_img = cv2.resize(cropped_img, (screen_width, screen_height))
        else:
            # Screen is taller than image, scale based on height (zoom in on width)
            scale = screen_height / img_height
            new_width = int(screen_width / scale)
            crop_x = (img_width - new_width) // 2
            cropped_img = img[:, crop_x:crop_x + new_width]
            result_img = cv2.resize(cropped_img, (screen_width, screen_height))
    else:
        # Calculate scaling factors and padding
        if screen_aspect_ratio > img_aspect_ratio:
            # Screen is wider than image, scale based on height
            scale = screen_height / img_height
            new_width = int(img_width * scale)
            padding = (screen_width - new_width) // 2
            scaled_img = cv2.resize(img, (new_width, screen_height))
            result_img = cv2.copyMakeBorder(scaled_img, 0, 0, padding, padding, cv2.BORDER_CONSTANT, value=(0, 0, 0))
        else:
            # Screen is taller than image, scale based on width
            scale = screen_width / img_width
            new_height = int(img_height * scale)
            padding = (screen_height - new_height) // 2
            scaled_img = cv2.resize(img, (screen_width, new_height))
            result_img = cv2.copyMakeBorder(scaled_img, padding, padding, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))

    if config['time_text']['show']:

        current_time = datetime.datetime.now().strftime(config['time_text']['format'])
        time_font_scale = config['time_text']['font_scale']
        time_font_thickness = config['time_text']['font_thickness']
        time_font_color = config['time_text']['font_color']

        # Get width and height of the time text
        time_width_and_height = cv2.getTextSize(current_time, cv2.FONT_HERSHEY_DUPLEX, time_font_scale, time_font_thickness)[0]
        time_width = time_width_and_height[0]
        time_height = time_width_and_height[1]

        if config['time_text']['relative_position']:
            if config['time_text']['relative_position'] == 'TOP_CENTER':
                time_x_position = (screen_width - time_width) // 2
                time_y_position = time_height + config['time_text']['margin_top']
            elif config['time_text']['relative_position'] == 'BOTTOM_CENTER':
                time_x_position = (screen_width - time_width) // 2
                time_y_position = screen_height - config['time_text']['margin_bottom']
            else:
                raise ValueError('Invalid value for time_text.relative_position')
        else:
            time_x_position = config['time_text']['start_position_X']
            time_y_position = screen_height - config['time_text']['start_position_Y']

        # Display time
        cv2.putText(result_img, current_time, (time_x_position, time_y_position), cv2.FONT_HERSHEY_DUPLEX, time_font_scale, time_font_color, time_font_thickness)

        if config['date_text']['show']:
            # Add date to the image
            current_date = datetime.datetime.now().strftime(config['date_text']['format'])

            date_font_scale = config['date_text']['font_scale']
            date_font_thickness = config['date_text']['font_thickness']
            date_font_color = config['date_text']['font_color']

            if config['date_text']['relative_position']:
                # Calculate width and height of the date text
                date_width_and_height = cv2.getTextSize(current_date, cv2.FONT_HERSHEY_DUPLEX, date_font_scale, date_font_thickness)[0]
                date_width = date_width_and_height[0]
                date_height = date_width_and_height[1]

                # Calculate where to start the date text in the x-axis so it's centered with the time text
                date_x_offset_from_time = round((time_width / 2) - (date_width / 2))

                spacing_from_time = config['date_text']['spacing_from_time']
                if config['date_text']['relative_position'] == 'CENTER_ABOVE_TIME':
                    date_x_position = time_x_position + date_x_offset_from_time
                    date_y_position = time_y_position - time_height - spacing_from_time

                elif config['date_text']['relative_position'] == 'CENTER_BELOW_TIME':
                    date_x_position = time_x_position + date_x_offset_from_time
                    date_y_position = time_y_position + date_height + spacing_from_time
                else:
                    raise ValueError('Invalid value for time_text.relative_position')
            else:
                date_x_position = config['date_text']['start_position_X']
                date_y_position = screen_height - config['date_text']['start_position_Y']

            # Display date
            cv2.putText(result_img, current_date, (date_x_position, date_y_position), cv2.FONT_HERSHEY_DUPLEX, date_font_scale, date_font_color, date_font_thickness)

    return result_img


def get_black_image(window_name):
    if config['slideshow']['display_width'] and config['slideshow']['display_height']:
        screen_width = config['slideshow']['display_width']
        screen_height = config['slideshow']['display_height']
    else:
        # Get if from the fullscreen window
        screen_width, screen_height = cv2.getWindowImageRect(window_name)[2:4]
    return np.zeros((screen_height, screen_width, 3), np.uint8)


def crossfade_images(img1, img2, alpha):
    img1 = cv2.resize(img1, (img2.shape[1], img2.shape[0]))
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    return cv2.addWeighted(img1, alpha, img2, 1 - alpha, 0)


def next_index(index, length):
    next_idx = index + 1
    if next_idx >= length:
        return 0
    return next_idx


async def async_download_photo(index, server_state):
    asyncio.create_task(
        download_random_photos(
            number_of_photos=1,
            photo_names=[str(index)],
            refresh_photos=False,
            server_state=server_state
        )
    )


def is_now_in_time_range(time_range):
    now = datetime.datetime.now().time()
    start_time = datetime.datetime.strptime(time_range['start'], '%H:%M').time()
    end_time = datetime.datetime.strptime(time_range['end'], '%H:%M').time()

    if start_time < end_time:
        return start_time <= now <= end_time
    else:  # Over midnight
        return now >= start_time or now <= end_time


def platform_is_windows():
    return platform.system() == 'Windows'


def set_brightness(brightness):
    if platform_is_windows():
        try:
            subprocess.run(['window_scripts/nircmd.exe', 'setbrightness', str(brightness)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to set brightness: {e}")


def show_black_photo(window_name):
    black_image = get_black_image(window_name)
    cv2.imshow(window_name, black_image)
    cv2.waitKey(10)


def handle_mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        window_height = cv2.getWindowImageRect(param['window_name'])[3]
        
        # Check if click is within the next photo area (top left corner)
        if (x <= config['next_click_area']['width'] and 
            y <= config['next_click_area']['height']):
            param['skip_to_next'] = True
            
        # Check if click is within the off area (bottom left corner)
        if (x <= config['off_click_area']['width'] and 
            y >= window_height - config['off_click_area']['height']):
            param['toggle_black_screen'] = True


def main_loop():
    # Check the platform. Used to determine if we can adjust the screen brightness
    os_is_windows = platform_is_windows()

    server_state = start_server()
    
    # Wait for the initial download to finish
    asyncio.run(download_random_photos(
        number_of_photos=5, 
        photo_names=["0", "1", "2", "3", "4"], 
        refresh_photos=config['general']['refresh_photos'],
        server_state=server_state
    ))

    delay_between_photos = config['slideshow']['delay_between_photos']
    transition_animation_duration = config['slideshow']['transition_animation_duration']

    image_folder = "photos/"  # Images destination
    images = os.listdir(image_folder)
    images.sort()
    number_of_images = len(images)

    window_name = "image"

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    if config['slideshow']['display_width'] == 0 or config['slideshow']['display_height'] == 0:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    
    click_params = {
        'window_name': window_name, 
        'skip_to_next': False,
        'toggle_black_screen': False
    }
    cv2.setMouseCallback(window_name, handle_mouse_click, click_params)

    current_brightness = 100
    current_img_index = 0
    black_screen_on = False
    pause_started = False
    pause_ended = False
    
    while True:
        # Check for HTTP toggle requests
        if server_state['toggle_black_screen_requested']:
            black_screen_on = not black_screen_on
            server_state['toggle_black_screen_requested'] = False
        
        # Trigger the black screen on pause start, and off on pause end
        if config['slideshow']['pause']['start'] and config['slideshow']['pause']['end']:
            if is_now_in_time_range(config['slideshow']['pause']):
                if not pause_started:
                    black_screen_on = True
                    pause_started = True
                    pause_ended = False
            else:
                if pause_started and not pause_ended:
                    black_screen_on = False
                    pause_started = False
                    pause_ended = True

        if black_screen_on:
            # If the user toggles the black screen, we need to continue the loop to show the next image
            if click_params['toggle_black_screen']:
                black_screen_on = not black_screen_on
                click_params['toggle_black_screen'] = False
            else:
            # Else show the black screen and lower the brightness
                show_black_photo(window_name)
                if current_brightness != 0:
                    set_brightness(0)
                    current_brightness = 0
            continue

        # Check if we need to adjust the brightness according the time of day (only for Windows)
        if os_is_windows and config['slideshow']['low_brightness']['start'] and config['slideshow']['low_brightness']['end']:
            low_brightness = config['slideshow']['low_brightness']['brightness']
            if is_now_in_time_range(config['slideshow']['low_brightness']):
                if current_brightness != low_brightness:
                    set_brightness(low_brightness)
                    current_brightness = low_brightness
            else:
                if current_brightness == low_brightness:
                    set_brightness(100)
                    current_brightness = 100

        # Image logic
        next_img_index = next_index(current_img_index, number_of_images)

        # Download image of the following iteration async so it's ready
        next_iteration_current_index = next_index(next_img_index, number_of_images)
        asyncio.run(async_download_photo(next_iteration_current_index, server_state))

        current_img_path = image_folder + images[current_img_index]
        next_img_path = image_folder + images[next_img_index]
        
        # Update current photo in server state
        server_state['current_photo'] = images[current_img_index]

        # Display the current image. If we are showing time, refresh every 2 seconds
        if config['time_text']['show']:
            number_of_refreshes = delay_between_photos // 2000  # Refresh every 2 seconds this many times
            for i in range(number_of_refreshes):
                cv2.imshow(window_name, get_fullscreen_image(current_img_path, window_name))
                key = cv2.waitKey(2000)
                if key == ord('q'):
                    break
                if click_params['skip_to_next']:
                    click_params['skip_to_next'] = False
                    break
                if click_params['toggle_black_screen']:
                    black_screen_on = not black_screen_on
                    click_params['toggle_black_screen'] = False
                    break
                if server_state['skip_to_next_requested']:
                    server_state['skip_to_next_requested'] = False
                    break  # This will exit the current iteration and move to the next photo
        
        else:
            cv2.imshow(window_name, get_fullscreen_image(current_img_path, window_name))
            key = cv2.waitKey(delay_between_photos)
            if key == ord('q'):
                break
            # TODO: This will not work since we are in the waitKey loop. Same thing for the manual black screen
            if click_params['skip_to_next']:
                click_params['skip_to_next'] = False

        if black_screen_on:
            continue

        fullscreen_current_img = get_fullscreen_image(current_img_path, window_name)
        fullscreen_next_img = get_fullscreen_image(next_img_path, window_name)

        # Crossfade to the next image
        for alpha in np.linspace(0, 1, transition_animation_duration // 10):
            blended_img = crossfade_images(fullscreen_next_img, fullscreen_current_img, alpha)
            cv2.imshow(window_name, blended_img)
            key = cv2.waitKey(10)
            if key == ord('q'):
                break

        current_img_index = next_index(current_img_index, number_of_images)


if __name__ == '__main__':
    try:
        print('Starting slideshow... Press "q" to quit.')
        main_loop()
    except Exception as e:
        traceback.print_exc()
        print("Something went wrong while running photo frame. Exiting...")
