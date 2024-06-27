import os
import logging
from pytube import YouTube
from moviepy.editor import AudioFileClip
from tkinter import messagebox

# It's good practice to configure logging at the beginning of your script
logging.basicConfig(level=logging.INFO)

class MP3Downloader:
    
    """
        MP3Downloader class is used to download YouTube videos as MP3 files. It provides methods to set the URL of the video, set the save path for the downloaded file, and download the video as an MP3.

        Attributes:
            url (str): The URL of the YouTube video.
            save_path (str): The path where the downloaded MP3 file will be saved.
            progress_callback (function): A callback function to track the progress of the download.

        Methods:
            __init__(self, url=None, save_path=None, progress_callback=None):
                Initializes a new instance of the MP3Downloader class.
                Args:
                    url (str, optional): The URL of the YouTube video. Defaults to None.
                    save_path (str, optional): The path where the downloaded MP3 file will be saved. Defaults to None.
                    progress_callback (function, optional): A callback function to track the progress of the download. Defaults to None.

            set_url(self, url):
                Sets the URL of the YouTube video.
                Args:
                    url (str): The URL of the YouTube video.

            set_path(self, save_path):
                Sets the save path for the downloaded MP3 file.
                Args:
                    save_path (str): The path where the downloaded MP3 file will be saved.

            get_default_download_path(self):
                Returns the default download path, typically the user's Downloads folder.

            download_as_mp3(self):
                Downloads the YouTube video as an MP3 file.
                Returns:
                    str: The path of the downloaded MP3 file.

        Raises:
            Exception: If the MP3 download and conversion fails.
    """
    
    def __init__(self, url=None, save_path=None, progress_callback=None):
        """
        Initializes the class instance with the provided URL, save path, and progress callback.

        Parameters:
            url (str): The URL to download from.
            save_path (str): The path to save the downloaded file to. Defaults to the user's Downloads folder if not specified.
            progress_callback (function): A callback function to track the download progress.
        """
        self.url = url
        # Set the default save_path to the user's Downloads folder if not specified
        self.save_path = save_path if save_path else self.get_default_download_path()
        self.progress_callback = progress_callback

    def set_url(self, url):
        """
        Set the URL for the object.

        Parameters:
            url (str): The URL to be set.

        Returns:
            None
        """
        self.url = url

    def set_path(self, save_path):
        """
        Set the path for saving files.

        Parameters:
            save_path (str): The path where files will be saved. If not provided, the default download path will be used.

        Returns:
            None
        """
        # Allow setting a new path; default to Downloads folder if not specified
        self.save_path = save_path if save_path else self.get_default_download_path()

    @staticmethod
    def get_default_download_path():
        """
        Get the default download path for the user's operating system.

        Returns:
            str: The default download path.
        """
        
        home_directory = os.path.expanduser('~')  # Get the home directory
        return os.path.join(home_directory, 'Downloads')

    def download_as_mp3(self):
        """
        Downloads the audio stream from a YouTube video as an MP3 file.

        Returns:
            str: The path to the downloaded MP3 file.

        Raises:
            Exception: If the MP3 download and conversion fails.
        """
        try:
            yt = YouTube(self.url)
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            final_file_path = os.path.join(self.save_path, yt.title.replace("/", "-") + ".mp3")
            
            logging.info(f"Downloading audio stream to: {final_file_path}")
            # Download the audio stream directly to the final location as mp4 or webm
            temp_file_path = audio_stream.download(output_path=self.save_path, filename=final_file_path)
            
            # Check if conversion is necessary (if the file is not already an mp3)
            if not final_file_path.endswith(".mp3"):
                logging.info(f"Converting to MP3: {final_file_path}")
                audio_clip = AudioFileClip(temp_file_path)
                audio_clip.write_audiofile(final_file_path)
                audio_clip.close()
                os.remove(temp_file_path)  # Remove the original download if conversion occurred
            
            logging.info(f"MP3 saved to: {final_file_path}")
            messagebox.showinfo("Success", "MP3 download and conversion successful.")
            return final_file_path
        except Exception as e:
            logging.error(f"MP3 download and conversion failed: {e}")
            messagebox.showerror("Error", f"MP3 download and conversion failed: {e}")
            raise
