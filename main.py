import datetime
import os

import cv2
import numpy as np

delay = 10000  # Delay duration in milliseconds
transition_duration = 1000  # Transition duration in milliseconds


def get_fullscreen_image(image_path, window_name):
    img = cv2.imread(image_path)

    # Get the dimensions of the image and the screen
    img_height, img_width = img.shape[:2]
    screen_width, screen_height = cv2.getWindowImageRect(window_name)[2:4]

    # Calculate aspect ratios
    img_aspect_ratio = img_width / img_height
    screen_aspect_ratio = screen_width / screen_height

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
        screen_height = new_height

    # Add time and date to image
    current_time = datetime.datetime.now().strftime("%H:%M")
    cv2.putText(result_img, current_time, (20, screen_height - 100), cv2.FONT_HERSHEY_DUPLEX, 5, (255, 255, 255), 5)

    return result_img


def crossfade_images(img1, img2, alpha):
    img1 = cv2.resize(img1, (img2.shape[1], img2.shape[0]))
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    return cv2.addWeighted(img1, alpha, img2, 1 - alpha, 0)

if __name__ == '__main__':

    image_folder = "photos/"  # Images destination
    images = os.listdir(image_folder)

    window_name = "image"

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    current_img_index = 0
    while True:
        current_img_index += 1

        if current_img_index >= len(images):
            current_img_index = 0

        next_img_index = current_img_index + 1
        if next_img_index >= len(images):
            next_img_index = 0

        current_img_path = image_folder + images[current_img_index]
        next_img_path = image_folder + images[next_img_index]

        fullscreen_current_img = get_fullscreen_image(current_img_path, window_name)
        fullscreen_next_img = get_fullscreen_image(next_img_path, window_name)

        # Display the image
        cv2.imshow(window_name, fullscreen_current_img)
        key = cv2.waitKey(delay)

        for alpha in np.linspace(0, 1, transition_duration // 10):
            blended_img = crossfade_images(fullscreen_next_img, fullscreen_current_img, alpha)
            cv2.imshow(window_name, blended_img)
            key = cv2.waitKey(10)
            if key == ord('q'):
                break

        if key == ord('q'):
            break
