import os
import tweepy
import urllib.request
import subprocess
from daemonize import Daemonize

# Define the Twitter account to watch
account_to_watch = "BMRF_ALERTS"

# Define the directory to save the downloaded videos
save_directory = "./videos/"

# Define the command to play the video
play_command = "vlc"

# Define the Twitter API credentials
consumer_key = "your_consumer_key"
consumer_secret = "your_consumer_secret"
access_token = "your_access_token"
access_token_secret = "your_access_token_secret"

# Define the PID file path for the daemon process
pid_file = "/var/run/twitter_video_downloader.pid"

# Define the function to run as the daemon process
def run():
    # Authenticate with the Twitter API
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # Create the save directory if it does not exist
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Define a listener to watch for new tweets
    class TwitterStreamListener(tweepy.StreamListener):
        def on_status(self, status):
            # Check if the tweet contains a video
            if hasattr(status, "extended_entities") and "media" in status.extended_entities:
                for media in status.extended_entities["media"]:
                    if media["type"] == "video":
                        # Download the video
                        video_url = media["video_info"]["variants"][0]["url"]
                        tweet_id = str(status.id)
                        file_name = save_directory + tweet_id + ".mp4"
                        urllib.request.urlretrieve(video_url, file_name)
                        print("Video downloaded:", file_name)

                        # Play the video
                        subprocess.Popen([play_command, file_name])

    # Start watching for new tweets
    twitter_stream_listener = TwitterStreamListener()
    twitter_stream = tweepy.Stream(auth=api.auth, listener=twitter_stream_listener)
    twitter_stream.filter(track=[account_to_watch], is_async=True)

# Define the arguments for the daemon process
daemon = Daemonize(app="twitter_video_downloader", pid=pid_file, action=run)

# Start the daemon process
daemon.start()
