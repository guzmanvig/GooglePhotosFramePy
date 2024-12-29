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

# Update to use the new Picker API scope
SCOPES = ['https://www.googleapis.com/auth/photospicker.mediaitems.readonly']


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


def create_picker_session():
    """Create a new Picker session for photo selection"""
    response = requests.post(
        "https://photospicker.googleapis.com/v1/sessions",
        headers={
            "Authorization": f"Bearer {get_token()}"
        },
        json={},
        timeout=30
    )
    
    if response.status_code != 200:
        raise ConnectionError(f"Error creating picker session: {response.status_code}")
        
    session_data = response.json()
    return session_data['id'], session_data['pickerUri']


def get_picked_media_items(session_id, page_token=None):
    """Get media items picked by user in a session"""
    params = {
        'sessionId': session_id,
        'pageSize': 100
    }
    if page_token:
        params['pageToken'] = page_token
        
    response = requests.get(
        "https://photospicker.googleapis.com/v1/mediaItems",
        params=params,
        headers={
            "Authorization": f"Bearer {get_token()}"
        },
        timeout=30
    )
    
    if response.status_code != 200:
        raise ConnectionError(f"Error getting picked media items: {response.status_code}")
        
    return response.json()


def get_all_media_items():
    """Get all media items using the Picker API"""
    # Create a new picker session
    session_id, picker_uri = create_picker_session()
    
    # Save the session ID for later use
    with open("picker_session.txt", "w") as f:
        f.write(session_id)
    
    print(f"Please visit this URL to select photos: {picker_uri}")
    input("Press Enter after you have finished selecting photos...")
    
    # Get all selected media items
    all_photo_ids = set()
    response = get_picked_media_items(session_id)
    
    while True:
        media_items = response.get('mediaItems', [])
        photo_ids = [item['id'] for item in media_items 
                    if item.get('type') == 'PHOTO']
        all_photo_ids.update(photo_ids)
        
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
            
        response = get_picked_media_items(session_id, next_page_token)
    
    # Clean up the session
    requests.delete(
        f"https://photospicker.googleapis.com/v1/sessions/{session_id}",
        headers={"Authorization": f"Bearer {get_token()}"},
        timeout=30
    )
    
    # Save the photo IDs
    with open("all_photo_ids.txt", "w") as f:
        for photo_id in all_photo_ids:
            f.write(f"{photo_id}\n")
    print("All photo ids have been retrieved and stored.")


@retry(wait=wait_random_exponential(min=3, max=20), stop=stop_after_attempt(3))
def download_photo(photo_name, photo_id, server_state):
    """Download a photo using the media item ID"""
    # Get the active session ID from a file or global variable
    with open("picker_session.txt", "r") as f:
        session_id = f.read().strip()
    
    response = requests.get(
        f"https://photospicker.googleapis.com/v1/mediaItems/{photo_id}",
        params={'sessionId': session_id},  # Add sessionId parameter
        headers={
            "Authorization": f"Bearer {get_token()}"
        }, 
        timeout=30
    )

    if response.status_code != 200:
        print(f"Error {response.status_code} - {response.reason} getting photo {photo_id}, trying again...")
        raise ConnectionError(f"Error while getting photo {photo_id}")

    data = response.json()
    base_url = data['mediaFile']['baseUrl']
    
    # Store the product URL in the server state if available
    if 'productUrl' in data:
        server_state['photo_urls'][f"{photo_name}.jpg"] = data['productUrl']
    
    response = requests.get(f"{base_url}=d", timeout=30)

    if response.status_code != 200:
        print(f"Error {response.status_code} - {response.reason} downloading photo {photo_id}, trying again...")
        raise ConnectionError(f"Error while getting photo {photo_id}")

    # Store the image
    with open(f"photos/{photo_name}.jpg", "wb") as f:
        f.write(response.content)


async def download_random_photos(number_of_photos, photo_names, refresh_photos=False, server_state=None):
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
        download_photo(photo_names[i], photo_id, server_state)

        # Test that the image was downloaded correctly. Try 3 times.
        img = cv2.imread(f"photos/{photo_names[i]}.jpg")
        while img is None and tries < 3:
            new_photo_id = np.random.choice(all_photo_ids, 1, replace=False)
            print(f"Invalid photo {photo_id}. Trying with photo {new_photo_id}...")
            download_photo(photo_names[i], new_photo_id, server_state)
            img = cv2.imread(f"photos/{photo_names[i]}.jpg")
            tries += 1
        if img is None:
            raise ConnectionError(f"Error downloading photos. Couldn't find a suitable photo.")


if __name__ == "__main__":
    asyncio.run(download_random_photos(3, ["0", "1", "2"]))





