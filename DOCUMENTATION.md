# Documentation

This document provides a detailed overview of the project's codebase.

## `GUI.py`

This file contains the main graphical user interface (GUI) for the application.

<details>
<summary>View Code</summary>

```python
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Text
import threading
from Mp4_Converter import YouTubeDownloader
from Mp3_Converter import MP3Downloader
from pathlib import Path

class YouTubeDownloaderGUI:
    def __init__(self, master):
        self.master = master
        self.downloader = None  
        self.default_download_path = str(Path.home() / "Downloads")
        self.build_gui()

    def build_gui(self):
        self.master.title('MP4/MP3 Downloader')
        self.master.geometry("650x550")
        self.master.resizable(False, False)

        # Style configuration
        style = ttk.Style(self.master)
        style.theme_use('clam')
        style.configure("TLabel", padding=6, font=('Helvetica', 10))
        style.configure("TButton", padding=6, font=('Helvetica', 10))
        style.configure("TEntry", padding=6, font=('Helvetica', 10))
        style.configure("TRadiobutton", font=('Helvetica', 10))
        style.configure("TMenubutton", font=('Helvetica', 10))

        # Main frame
        main_frame = ttk.Frame(self.master, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # URL and Path Frame
        url_path_frame = ttk.LabelFrame(main_frame, text="Input", padding="10 10 10 10")
        url_path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_path_frame, text="YouTube URL:").grid(row=0, column=0, sticky="w", pady=2)
        self.url_entry = ttk.Entry(url_path_frame, width=60)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)

        ttk.Label(url_path_frame, text="Download Path:").grid(row=1, column=0, sticky="w", pady=2)
        self.path_display = ttk.Entry(url_path_frame, width=50)
        self.path_display.grid(row=1, column=1, sticky="ew", pady=2)
        self.browse_button = ttk.Button(url_path_frame, text="Browse", command=self.browse_path)
        self.browse_button.grid(row=1, column=2, sticky="e", padx=5, pady=2)
        
        url_path_frame.columnconfigure(1, weight=1)

        # Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10 10 10 10")
        options_frame.pack(fill=tk.X, pady=5)

        ttk.Label(options_frame, text="Format:").grid(row=0, column=0, sticky="w")
        self.format_var = tk.StringVar(value="MP4")
        self.mp4_radio = ttk.Radiobutton(options_frame, text="MP4", variable=self.format_var, value="MP4", command=self.update_format_color)
        self.mp4_radio.grid(row=0, column=1, sticky='w', padx=5)
        self.mp3_radio = ttk.Radiobutton(options_frame, text="MP3", variable=self.format_var, value="MP3", command=self.update_format_color)
        self.mp3_radio.grid(row=0, column=2, sticky='w', padx=5)

        ttk.Label(options_frame, text="Resolution:").grid(row=1, column=0, sticky="w")
        self.resolution_var = tk.StringVar(self.master)
        self.resolution_menu = ttk.OptionMenu(options_frame, self.resolution_var, "Highest")
        self.resolution_menu.grid(row=1, column=1, columnspan=2, sticky="w", pady=5)

        # Controls Frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)

        self.download_button = ttk.Button(controls_frame, text="Download", command=self.start_download)
        self.download_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.close_button = ttk.Button(controls_frame, text="Close", command=self.master.destroy)
        self.close_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # Progress and Log Frame
        progress_log_frame = ttk.LabelFrame(main_frame, text="Status", padding="10 10 10 10")
        progress_log_frame.pack(expand=True, fill=tk.BOTH, pady=5)

        self.progress = ttk.Progressbar(progress_log_frame, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        self.message_screen = Text(progress_log_frame, height=10, width=75, font=('Courier', 9), fg='black', bg='#f0f0f0')
        self.message_screen.pack(expand=True, fill=tk.BOTH, pady=5)
        self.message_screen.config(state=tk.DISABLED)

        self.update_format_color()
        self.last_checked_url = ""
        self.master.after(1000, self.auto_fetch_resolutions)

    def auto_fetch_resolutions(self):
        current_url = self.url_entry.get()
        if current_url and current_url != self.last_checked_url:
            self.last_checked_url = current_url
            # Run fetching in a separate thread to not block the GUI
            threading.Thread(target=self.fetch_resolutions, daemon=True).start()
        self.master.after(1000, self.auto_fetch_resolutions) # Check again in 1 second

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_display.delete(0, tk.END)
            self.path_display.insert(0, path)

    def fetch_resolutions(self):
        url = self.last_checked_url # Use the last checked URL
        if not url:
            return # Silently return if no URL

        try:
            downloader = YouTubeDownloader()
            downloader.set_url(url)
            info = downloader.fetch_video_info()
            formats = info.get('formats', [])
            resolutions = sorted(list(set([f['height'] for f in formats if f.get('height') and f.get('vcodec') != 'none'])), reverse=True)
            
            if not resolutions:
                messagebox.showinfo("Info", "No video resolutions found.")
                return

            self.resolution_var.set(resolutions[0]) # Default to highest
            menu = self.resolution_menu['menu']
            menu.delete(0, 'end')
            for res in resolutions:
                menu.add_command(label=f"{res}p", command=lambda value=res: self.resolution_var.set(value))
            
            self.log_message("Resolutions fetched successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch resolutions: {e}")

    def start_download(self):
        self.progress['value'] = 0
        self.progress.update()

        url = self.url_entry.get()
        path = self.path_display.get() or self.default_download_path

        if self.format_var.get() == "MP4":
            resolution = self.resolution_var.get()
            if not resolution:
                messagebox.showerror("Error", "Please fetch and select a resolution.")
                return
            self.downloader = YouTubeDownloader(self.update_progress, self.log_message)
            self.downloader.set_url(url)
            self.downloader.set_path(path)
            self.downloader.resolution = int(resolution)
            download_thread = threading.Thread(target=self.downloader.download_video)
        elif self.format_var.get() == "MP3":
            self.downloader = MP3Downloader(url, path, self.update_progress, self.log_message)
            download_thread = threading.Thread(target=self.downloader.download_as_mp3)
        download_thread.start()

    def update_progress(self, percentage):
        self.progress['value'] = percentage
        self.progress.update()
        if percentage == 100:
            self.master.after(3000, self.clear_progress_bar)

    def clear_progress_bar(self):
        self.progress['value'] = 0
        self.progress.update()

    def log_message(self, message):
        self.message_screen.config(state=tk.NORMAL)
        self.message_screen.insert(tk.END, message + "\n")
        self.message_screen.see(tk.END)
        self.message_screen.config(state=tk.DISABLED)

    def update_format_color(self):
        # This can be expanded to disable/enable the resolution dropdown
        is_mp4 = self.format_var.get() == "MP4"
        self.resolution_menu.config(state=tk.NORMAL if is_mp4 else tk.DISABLED)

def run_gui():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
```
</details>


---

## `Mp4_Converter.py`

This file handles the downloading and conversion of YouTube videos to MP4 format.

<details>
<summary>View Code</summary>

```python
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
```
</details>

---

## `Mp3_Converter.py`

This file handles the downloading and conversion of YouTube videos to MP3 format.

<details>
<summary>View Code</summary>

```python
import os
import logging
import yt_dlp
from tkinter import messagebox

logging.basicConfig(level=logging.INFO)

class MP3Downloader:
    def __init__(self, url=None, save_path=None, progress_callback=None, log_callback=None):
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
        self.log_callback = log_callback

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
            with yt_dlp.YoutubeDL({}) as ydl:
                info = ydl.extract_info(self.url, download=False)
                title = info.get('title', 'Unknown Title')

            if self.log_callback:
                self.log_callback(f"Download started: \"{title}\" - Format: MP3. Saved at: \"{self.save_path}\"")

            options = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(self.save_path, f'{title}.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'keepvideo': True,
            }
            
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([self.url])
            
            if self.log_callback:
                self.log_callback(f"Download complete at {self.save_path}")

            return self.save_path
        except Exception as e:
            if self.log_callback:
                self.log_callback(f"An error occurred: {e}")
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
```
</details>
