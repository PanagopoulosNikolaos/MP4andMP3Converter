from pytube import YouTube
from pytube.cli import on_progress
import os
import threading




class YouTubeDownloader:
    """
        YouTubeDownloader class for downloading videos from YouTube.

        This class provides methods to set the URL of the video to be downloaded, set the download path, and download the video.
        It also supports a progress callback function to track the progress of the download.

        Attributes:
            url (str): The URL of the video to be downloaded.
            path (str): The path where the video will be saved.
            progress_callback (function): A callback function to track the progress of the download.

        Methods:
            __init__(self, progress_callback=None): Initializes a new instance of the YouTubeDownloader class.
            get_default_download_path(): Returns the default download path (the user's Downloads folder).
            set_url(self, url): Sets the URL of the video to be downloaded.
            set_path(self, path): Sets the download path.
            download_video(self): Downloads the video from the specified URL.
            on_progress(self, stream, chunk, bytes_remaining): Callback function to track the progress of the download.

        Example usage:
            downloader = YouTubeDownloader()
            downloader.set_url('https://www.youtube.com/watch?v=VIDEO_ID')
            downloader.set_path('/path/to/save/video')
            downloader.download_video()

            def progress_callback(percentage):
                print(f"Download progress: {percentage}%")

            downloader = YouTubeDownloader(progress_callback)
            downloader.set_url('https://www.youtube.com/watch?v=VIDEO_ID')
            downloader.set_path('/path/to/save/video')
            downloader.download_video()
    """
    def __init__(self, progress_callback=None):
        """
        Initialize the object with an optional progress_callback.

        Parameters:
            progress_callback (function): A function to be called with progress updates.

        Returns:
            None
        """
        self.url = None
        # Use the get_default_download_path method to set a default path if none is provided
        self.path = self.get_default_download_path()
        self.progress_callback = progress_callback

    @staticmethod
    def get_default_download_path():
        """
        A static method to get the default download path.
        """
        
        home_directory = os.path.expanduser('~')  # Get the home directory
        return os.path.join(home_directory, 'Downloads')

    def set_url(self, url):
        """
        Set the URL for the object.

        :param url: The URL to be set.
        :return: None
        """
        self.url = url

    def set_path(self, path):
        """
        Set the path for downloading files.

        Parameters:
            path (str): The path to set for downloading files.

        Returns:
            None
        """
        # If no valid path is provided, use the default Downloads directory
        self.path = path if path else self.get_default_download_path()
        
        # Ensure the save path exists, if not, create it
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def download_video(self):
        try:
            yt = YouTube(self.url, on_progress_callback=self.on_progress)

            # Fetch the best quality stream that includes both audio and video
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

            if stream:
                # Download the video
                stream.download(output_path=self.path)
                print(f"Video has been downloaded and saved to {self.path}")
            else:
                print("No suitable stream available.")
        except Exception as e:
            print(f"An error occurred: {e}")


    def on_progress(self, stream, chunk, bytes_remaining):
        """
        Updates the progress of a download by calculating the percentage of bytes downloaded and invoking the progress callback.

        Parameters:
            stream (Stream): The stream object representing the download.
            chunk (bytes): The chunk of data that has been downloaded.
            bytes_remaining (int): The number of bytes remaining to be downloaded.

        Returns:
            None
        """
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining 
        percentage = int((bytes_downloaded / total_size) * 100)
        if self.progress_callback:
            self.progress_callback(percentage)






