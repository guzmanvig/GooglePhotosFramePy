import asyncio
import os.path

import cv2
from tenacity import retry, wait_random_exponential, stop_after_attempt
import numpy as np
import requests
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from config import config

SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

all_photo_ids = []


def get_token():
    if not os.path.exists("client_secret.json"):
        raise FileNotFoundError("Google Project credentials not found. Create them and save them as client_secret.json")

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as e:
                os.remove("token.json")
                flow = InstalledAppFlow.from_client_secrets_file(
                    "client_secret.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds.token


def google_api_search(page_token):
    date_ranges = config['photo_selection']['ranges']

    response = requests.post(
        "https://photoslibrary.googleapis.com/v1/mediaItems:search",
        headers={
            "Authorization": f"Bearer {get_token()}"
        },
        json={
            "filters": {
                "dateFilter": {
                    "ranges": date_ranges
                },
                "mediaTypeFilter": {
                    "mediaTypes": ["PHOTO"]
                }
            },
            "pageSize": 100,
            "pageToken": page_token
        },
        timeout=30
    )

    response_json = response.json()
    media_items = response_json["mediaItems"]
    next_page_token = response_json.get("nextPageToken")

    photo_ids = [photo["id"] for photo in media_items]
    return photo_ids, next_page_token


def get_all_media_items():
    photo_ids, next_page_token = google_api_search("")
    all_photo_ids.extend(photo_ids)
    page = 1
    while next_page_token:
        print(f"Getting Google Photos page {page}...")
        photo_ids, next_page_token = google_api_search(next_page_token)
        all_photo_ids.extend(photo_ids)
        page += 1
    print("All photos have been retrieved.")


@retry(wait=wait_random_exponential(min=3, max=20), stop=stop_after_attempt(3))
def download_photo(photo_name, photo_id):
    response = requests.get(f"https://photoslibrary.googleapis.com/v1/mediaItems/{photo_id}",
                            headers={
                                    "Authorization": f"Bearer {get_token()}"
                                }, timeout=30)

    if response.status_code != 200:
        print(f"Error {response.status_code} - {response.reason} getting photo {photo_id}, trying again...")
        raise ConnectionError(f"Error while getting photo {photo_id}")

    data = response.json()
    base_url = data["baseUrl"]
    response = requests.get(f"{base_url}=d", timeout=30)

    if response.status_code != 200:
        print(f"Error {response.status_code} - {response.reason} downloading photo {photo_id}, trying again...")
        raise ConnectionError(f"Error while getting photo {photo_id}")

    # Store the image
    with open(f"photos/{photo_name}.jpg", "wb") as f:
        f.write(response.content)

    # Test that the image was downloaded correctly
    img = cv2.imread(f"photos/{photo_name}.jpg")
    if img is None:
        print(f"Error while reading photo {photo_id}, trying again...")
        raise ConnectionError(f"Error while reading photo {photo_id}")


async def download_random_photos(number_of_photos, photo_names):
    if len(photo_names) != number_of_photos:
        raise ValueError("The number of photo names should be equal to the number of photos")

    if len(all_photo_ids) < number_of_photos:
        raise ValueError("There are not enough photos to select from.")

    # Select random photos links
    random_photos_ids = np.random.choice(all_photo_ids, number_of_photos, replace=False)

    # Create directory for photos if it doesn't exist
    if not os.path.exists('photos'):
        os.makedirs('photos')

    # Download the photos
    for i, photo_id in enumerate(random_photos_ids):
        download_photo(photo_names[i], photo_id, all_photo_ids)


if __name__ == "__main__":
    asyncio.run(download_random_photos(3, ["0", "1", "2"]))





