# GooglePhotosFramePy: A Google Photos Frame in Python

This is a Google Photos Frame in Python. It uses the Google Photos API to get the photos and display them randomly in fullscreen.

Check `config.py` for the full configuration options.

## My use case

I have an old Windows tablet that is pretty much useless. I couldn't find any available software that would turn it into a digital photo frame that would display my Google Photos. So I decided to create my own.

insert gif here

## Potential new features

At the moment, the app serves the purpose I needed it for. However, there are some features that could be added to make it more useful for other people.
I'm down to do them if someone requests them.

- [ ] Create a Batch script for Windows to start the program (or Bash for Linux) and/or package it
- [ ] Support other operating systems (macOS, Linux, mobile) (Note: At the moment I only tried it in Windows, perhaps MacOS and Linux already work)
- [ ] Better error handling, especially for when losing connection
- [ ] Windows scheduler to start the app when the computer starts and turn off at night
- [ ] Add album selection support
- [ ] Display metadata of photos (like the photo date)
- [ ] Support videos
- [ ] Support multiple accounts
- [ ] Support other cloud services (Dropbox, OneDrive, etc) and local photos
- [ ] Support other transition animations
- [ ] Support other ways to display the photos (zoomed, cropped, etc)
- [ ] Support other strategies to display the photos (instead of random, like ordered by date for example)

If  you need one of these features (or other), feel free to open an issue or a pull request, or contact me at
guzmanvigliecca@gmail.com


## How to run

Because this app is not officially published in Google yet, you need to create your own project and credentials. 

1 - Go to the Google Developers Console and create a new project.

2 - Enable the Google Photos API.

3 - Enable the photoslibrary.readonly scope.

4 - Set up the OAuth consent screen (you can set it up with minimal information since you will not publish the app).

5 - Add your email as a test user.

6 - Create credentials for a desktop app.

7 - Download the credentials file and save it as `client_secret.json` in the root folder of this project.

Once this is done, create a virtual environment and install the requirements:

1 - Run `python -m venv venv` to create a virtual environment.

2 - Run `venv\Scripts\activate` to activate the virtual environment (this is for Windows, for Unix run `source venv/bin/activate`).

3 - Run `pip install -r requirements.txt` to install the requirements.

Then, run the following to start the app: `python main.py`.

## How to use
Take a look at `config.py` to see all the configuration options and modify it as you wish.

The first time you run the app, it will open a browser window asking you to log in to your Google account. 
Then, the app will get all the photos download links from the date ranges you set in the `config.py` file, this can
take a while depending on the number of photos you have. Then, it will display it in fullscreen randomly.

To quit the app press `q` (repeatedly if needed).
