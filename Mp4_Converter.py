

import os
import yt_dlp
import logging

class YouTubeDownloader:
    def __init__(self, progress_callback=None, log_callback=None):
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
        self.log_callback = log_callback
        self.video_title = None
        self.resolution = None

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
        if not self.url:
            raise ValueError("URL is not set. Use set_url() method to set the URL before downloading.")

        try:
            info = self._get_video_info()
            self.video_title = info.get('title', 'Unknown Title')
            self.resolution = info.get('height', 'Unknown Resolution')

            if self.log_callback:
                self.log_callback(f"Download started: \"{self.video_title}\" - Resolution: {self.resolution}p. Saved at: \"{self.path}\"")

            # Download audio
            self._download_stream('bestaudio', 'audio_temp', 0, 50)
            # Download video
            self._download_stream(f'bestvideo[height<={self.resolution}]', 'video_temp', 50, 100)

            self._merge_files()

            if self.log_callback:
                self.log_callback(f"Download complete at {self.path}")

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            if self.log_callback:
                self.log_callback(f"An error occurred: {e}")

    def fetch_video_info(self):
        """
        Fetches video information without downloading.
        This method is intended to be called from the GUI to populate resolution choices.
        """
        if not self.url:
            raise ValueError("URL is not set.")
        with yt_dlp.YoutubeDL({}) as ydl:
            return ydl.extract_info(self.url, download=False)

    def _get_video_info(self):
        return self.fetch_video_info()

    def _download_stream(self, format_selection, temp_filename, start_progress, end_progress):
        options = {
            'format': format_selection,
            'outtmpl': os.path.join(self.path, f'{temp_filename}.%(ext)s'),
            'progress_hooks': [lambda d: self._progress_hook(d, start_progress, end_progress)],
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([self.url])

    def _merge_files(self):
        if self.log_callback:
            self.log_callback("Merging audio and video...")
        
        # Find temporary files
        temp_files = [f for f in os.listdir(self.path) if f.startswith('video_temp') or f.startswith('audio_temp')]
        video_file = next((f for f in temp_files if f.startswith('video_temp')), None)
        audio_file = next((f for f in temp_files if f.startswith('audio_temp')), None)

        if not video_file or not audio_file:
            if self.log_callback:
                self.log_callback("Error: Could not find temporary audio/video files to merge.")
            return

        video_path = os.path.join(self.path, video_file)
        audio_path = os.path.join(self.path, audio_file)
        output_path = os.path.join(self.path, f"{self.video_title}.mp4")

        # Use ffmpeg to merge
        command = f"ffmpeg -i \"{video_path}\" -i \"{audio_path}\" -c:v copy -c:a aac \"{output_path}\""
        
        try:
            os.system(command)
            if self.log_callback:
                self.log_callback("Files merged successfully.")
        except Exception as e:
            if self.log_callback:
                self.log_callback(f"Error during merge: {e}")
        finally:
            # Clean up temporary files
            os.remove(video_path)
            os.remove(audio_path)

    def _progress_hook(self, d, start_progress, end_progress):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                percentage = (downloaded_bytes / total_bytes) * 100
                scaled_progress = start_progress + (percentage / 100) * (end_progress - start_progress)
                if self.progress_callback:
                    self.progress_callback(int(scaled_progress))
        elif d['status'] == 'finished':
            if self.progress_callback:
                self.progress_callback(end_progress)
