# GooglePhotosFramePy: A Configurable Google Photos Frame in Python

This is a Google Photos Frame in Python. It uses the Google Photos API to get the photos and display them randomly in fullscreen.

Has a bunch of configuration options such as displaying time and date, pausing, dim brightness, etc. Check `config.py` for the full configuration options.

Tested in: Windows 10, Ubuntu 20, MacOS 14.5

## My use case

I have an old Windows tablet that is pretty much useless. I couldn't find any free, open-source, software that would turn it into a digital photo frame that would display my Google Photos. So I decided to create my own.

![demo](https://github.com/guzmanvig/GooglePhotosFramePy/blob/main/demo.gif)

## Potential new features

At the moment, the app serves the purpose I needed it for. However, there are some features that could be added to make it more useful for other people.
I'm down to do them if someone requests them.

- [x] Create a Batch script for Windows to start the program (or Bash for Linux).
- [x] Support other operating systems (macOS, Linux)
- [x] Better error handling, especially for when losing connection
- [x] Windows scheduler to start the app when the computer starts and turn off at night
- [x] Added configurable pause and brightness dim
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

Pre-requisite: Python 3.12 installed (didn't test lower versions, but it's possible it works too)

### Google Photos API setup

Because this app is not officially published in Google yet, you need to create your own project and credentials. 

1 - Go to the Google Developers Console and create a new project.

2 - Enable the Google Photos API.

3 - Enable the photoslibrary.readonly scope.

4 - Set up the OAuth consent screen (you can set it up with minimal information since you will not publish the app).

5 - Add your email as a test user.

6 - Create credentials for a desktop app.

7 - Download the credentials file and save it as `client_secret.json` in the root folder of this project.

### Running the app

Once the previous step is done, run `bash run.sh` if you are in Linux/MacOS or `.\run.bat` if you are in Windows. This should start the program.
The first time the scripts run, the requirements are installed so it may take some time.

You can also manually create a virtual environment and install the requirements (which is exactly what the scripts do):

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

Note: If you don't see the slideshow in fullscreen, try specifying your screen resolution in the `display_width` and `display_height` fields in the config file.
