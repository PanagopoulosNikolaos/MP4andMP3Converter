
import os
import yt_dlp

class YouTubeDownloader:
    def __init__(self, progress_callback=None):
        """
        Initializes a YouTubeDownloader object.

        Parameters
        ----------
        progress_callback : callable or None
            A function that takes a single argument, an integer representing the download progress percentage,
            that will be called every time the download progress changes. If None, no callback is used.

        Attributes
        ----------
        url : str or None
            The URL of the YouTube video to download. Set to None initially.
        path : str
            The path where the downloaded video will be saved. Defaults to the user's home directory, in a folder named
            'Downloads'.
        progress_callback : callable or None
            A function that takes a single argument, an integer representing the download progress percentage,
            that will be called every time the download progress changes. If None, no callback is used.
        """
        self.url = None
        self.path = self.get_default_download_path()
        self.progress_callback = progress_callback

    @staticmethod
    def get_default_download_path():
        """
        Returns the default path where downloaded videos will be saved.

        The default path is set to the user's home directory, in a folder named 'Downloads'.
        """
        home_directory = os.path.expanduser('~')
        return os.path.join(home_directory, 'Downloads')

    def set_url(self, url):
        """
        Sets the URL of the YouTube video to download.

        Parameters
        ----------
        url : str
            The URL of the YouTube video to download.

        Returns
        -------
        None
        """

        self.url = url

    def set_path(self, path):
        """
        Sets the path where the downloaded video will be saved.

        Parameters
        ----------
        path : str or None
            The path where the downloaded video will be saved. If None, the default path (user's home directory, in a
            folder named 'Downloads') is used.

        Returns
        -------
        None
        """
        self.path = path if path else self.get_default_download_path()
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def download_video(self):
        """
        Downloads the video from the set URL to the set path.

        Raises
        ------
        ValueError
            If the URL is not set. Use set_url() method to set the URL before downloading.

        Returns
        -------
        None
        """
        
        if not self.url:
            raise ValueError("URL is not set. Use set_url() method to set the URL before downloading.")

        options = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(self.path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'progress_hooks': [self.progress_hook],
        }

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([self.url])
            print(f"Video has been downloaded and saved to {self.path}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                percentage = (downloaded_bytes / total_bytes) * 100
                if self.progress_callback:
                    self.progress_callback(int(percentage))
        elif d['status'] == 'finished':
            if self.progress_callback:
                self.progress_callback(100)
