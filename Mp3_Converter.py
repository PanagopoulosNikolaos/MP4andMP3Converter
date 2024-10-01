import os
import logging
import yt_dlp
from tkinter import messagebox

logging.basicConfig(level=logging.INFO)

class MP3Downloader:
    def __init__(self, url=None, save_path=None, progress_callback=None):
        """
        Initializes an instance of the MP3Downloader class.

        Parameters
        ----------
        url : str, optional
            The URL of the YouTube video to download. If not provided, must be set using set_url() before downloading.
        save_path : str, optional
            The path where the downloaded MP3 file will be saved. If not provided, defaults to the user's home directory.
        progress_callback : function, optional
            A function that will be called with the percentage of download progress as an argument. If not provided, no progress messages will be displayed.

        Returns
        -------
        None
        """
        self.url = url
        self.save_path = save_path if save_path else self.get_default_download_path()
        self.progress_callback = progress_callback

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

    def set_path(self, save_path):
        """
        Sets the path where the downloaded MP3 file will be saved.

        Parameters
        ----------
        save_path : str, optional
            The path where the downloaded MP3 file will be saved. If not provided, defaults to the user's home directory.

        Returns
        -------
        None
        """
        self.save_path = save_path if save_path else self.get_default_download_path()

    @staticmethod
    def get_default_download_path():
        """
        Returns the default path where downloaded files are saved.

        Returns
        -------
        str
            The default path where downloaded files are saved. This is the user's home directory.
        """
        home_directory = os.path.expanduser('~')
        return os.path.join(home_directory, 'Downloads')

    def download_as_mp3(self):

        """
        Downloads the audio from a YouTube video as an MP3 file and saves it to the path set by set_path() or the default path.

        Parameters
        ----------
        None

        Returns
        -------
        str
            The path where the downloaded MP3 file was saved.

        Raises
        ------
        Exception
            If the download and conversion fails, an exception is raised with a message describing the error.
        """
        try:
            options = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }
            
            with yt_dlp.YoutubeDL(options) as ydl:
                logging.info(f"Downloading audio from: {self.url}")
                ydl.download([self.url])
            
            logging.info(f"MP3 downloaded successfully to: {self.save_path}")
            messagebox.showinfo("Success", "MP3 download and conversion successful.")
            return self.save_path
        except Exception as e:
            logging.error(f"MP3 download and conversion failed: {e}")
            messagebox.showerror("Error", f"MP3 download and conversion failed: {e}")
            raise

    def progress_hook(self, d):
        """
        Updates the progress bar in the GUI with the given percentage value.

        Parameters
        ----------
        d : dict
            A dictionary with information about the download progress.

        Notes
        -----
        If the status is 'downloading', the progress bar is updated with a percentage value calculated from the total_bytes and downloaded_bytes.
        If the status is 'finished', the progress bar is set to 100%.
        """

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
