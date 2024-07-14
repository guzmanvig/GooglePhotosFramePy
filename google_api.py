import asyncio
import datetime
import os.path

import numpy as np
import pandas as pd
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']


def get_token():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds.token


async def download_random_photos(number_of_photos, photo_names):
    # Create 50 random dates between 2018-01-01 and today
    dates = pd.date_range(start='2018-01-01', end=datetime.datetime.now().strftime("%Y-%m-%d"), periods=50)
    # Create 4 random indices between 0 and the length of the dates - 1
    random_start_dates_indices = np.random.randint(0, len(dates) - 1, 4)

    date_ranges = []
    for i in random_start_dates_indices:
        start_date = dates[i]
        end_date = dates[i + 1]
        date_ranges.append({
            "startDate": {"year": start_date.year, "month": start_date.month, "day": start_date.day},
            "endDate": {"year": end_date.year, "month": end_date.month, "day": end_date.day}
        })

    # Get photos based on the random range of dates
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
            }
        }
    )

    response_json = response.json()
    media_items = response_json["mediaItems"]

    # Select 4 random photos
    random_photos = np.random.choice(media_items, number_of_photos)

    # Download the photos
    for i, photo in enumerate(random_photos):
        response = requests.get(f"{photo['baseUrl']}=d")
        with open(f"photos/{photo_names[i]}.jpg", "wb") as f:
            f.write(response.content)


if __name__ == "__main__":
    asyncio.run(download_random_photos(3, ["0", "1", "2"]))





