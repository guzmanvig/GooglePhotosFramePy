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


def google_api_media_search(page_token, date_ranges, album_id):
    payload = {
            "pageSize": 100,
            "pageToken": page_token
    }
    if album_id:
        payload["albumId"] = album_id
    else:
        payload["filters"] = {
                "dateFilter": {
                    "ranges": date_ranges
                }
        }

    response = requests.post(
        "https://photoslibrary.googleapis.com/v1/mediaItems:search",
        headers={
            "Authorization": f"Bearer {get_token()}"
        },
        json=payload,
        timeout=30
    )

    response_json = response.json()
    media_items = response_json.get("mediaItems", None)
    if not media_items:
        return [], None

    next_page_token = response_json.get("nextPageToken")
    photo_ids = [photo["id"] for photo in media_items if photo["mimeType"].startswith("image/")]
    return photo_ids, next_page_token


def google_api_album_search(page_token, shared_albums, album_names):
    if shared_albums:
        url = "https://photoslibrary.googleapis.com/v1/sharedAlbums"
    else:
        url = "https://photoslibrary.googleapis.com/v1/albums"

    response = requests.get(
        url,
        params={
            "pageSize": 50,
            "pageToken": page_token
        },
        headers={
            "Authorization": f"Bearer {get_token()}"
        },
        timeout=30
    )

    response_json = response.json()
    albums = response_json["albums"] if not shared_albums else response_json["sharedAlbums"]
    next_page_token = response_json.get("nextPageToken")

    if len(album_names) == 1 and album_names[0] == "ALL":
        album_ids = [album["id"] for album in albums]
    else:
        album_ids = [album["id"] for album in albums if album.get("title", None) in album_names]
    return album_ids, next_page_token


def get_all_media_items():
    all_album_ids = set()

    # Get all the album ids
    albums = config['photo_selection'].get('albums', None)
    if albums and len(albums) != 0:
        album_ids, next_page_token = google_api_album_search(page_token="", shared_albums=False, album_names=albums)
        all_album_ids.update(album_ids)
        page = 1
        while next_page_token:
            print(f"Getting Google Photos albums page {page}...")
            album_ids, next_page_token = google_api_album_search(page_token=next_page_token, shared_albums=False, album_names=albums)
            all_album_ids.update(album_ids)
            page += 1

    # Get all the shared album ids
    shared_albums = config['photo_selection'].get('shared_albums', None)
    if shared_albums and len(shared_albums) != 0:
        album_ids, next_page_token = google_api_album_search(page_token="", shared_albums=True, album_names=shared_albums)
        all_album_ids.update(album_ids)
        page = 1
        while next_page_token:
            print(f"Getting Google Photos shared albums page {page}...")
            album_ids, next_page_token = google_api_album_search(page_token=next_page_token, shared_albums=True, album_names=shared_albums)
            all_album_ids.update(album_ids)
            page += 1

    all_photo_ids = set()

    # Get all the media items from the albums
    if len(all_album_ids) != 0:
        for album_id in all_album_ids:
            photo_ids, next_page_token = google_api_media_search(page_token="", date_ranges=[], album_id=album_id)
            all_photo_ids.update(photo_ids)
            page = 1
            while next_page_token:
                print(f"Getting Google Photos from album page {page}...")
                photo_ids, next_page_token = google_api_media_search(page_token=next_page_token, date_ranges=[], album_id=album_id)
                all_photo_ids.update(photo_ids)
                page += 1

    # Get all the media items from the date ranges
    date_ranges = config['photo_selection']['ranges']
    if date_ranges and date_ranges != []:
        photo_ids, next_page_token = google_api_media_search(page_token="", date_ranges=date_ranges, album_id=None)
        all_photo_ids.update(photo_ids)
        page = 1
        while next_page_token:
            print(f"Getting Google Photos from date ranges page {page}...")
            photo_ids, next_page_token = google_api_media_search(page_token=next_page_token, date_ranges=date_ranges, album_id=None)
            all_photo_ids.update(photo_ids)
            page += 1

    with open("all_photo_ids.txt", "w") as f:
        for photo_id in all_photo_ids:
            f.write(f"{photo_id}\n")
    print("All photo ids have been retrieved and stored.")


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


async def download_random_photos(number_of_photos, photo_names, refresh_photos=False):
    if len(photo_names) != number_of_photos:
        raise ValueError("The number of photo names should be equal to the number of photos")

    if not os.path.exists("all_photo_ids.txt") or refresh_photos:
        get_all_media_items()

    with open("all_photo_ids.txt", "r") as f:
        all_photo_ids = f.read().splitlines()

    if len(all_photo_ids) < number_of_photos:
        raise ValueError("There are not enough photos to select from.")

    # Select random photos links
    random_photos_ids = np.random.choice(all_photo_ids, number_of_photos, replace=False)

    # Create directory for photos if it doesn't exist
    if not os.path.exists('photos'):
        os.makedirs('photos')

    # Download the photos
    for i, photo_id in enumerate(random_photos_ids):
        tries = 0
        download_photo(photo_names[i], photo_id)

        # Test that the image was downloaded correctly. Try 3 times.
        img = cv2.imread(f"photos/{photo_names[i]}.jpg")
        while img is None and tries < 3:
            new_photo_id = np.random.choice(all_photo_ids, 1, replace=False)
            print(f"Invalid photo {photo_id}. Trying with photo {new_photo_id}...")
            download_photo(photo_names[i], new_photo_id)
            img = cv2.imread(f"photos/{photo_names[i]}.jpg")
            tries += 1
        if img is None:
            raise ConnectionError(f"Error downloading photos. Couldn't find a suitable photo.")


if __name__ == "__main__":
    asyncio.run(download_random_photos(3, ["0", "1", "2"]))





