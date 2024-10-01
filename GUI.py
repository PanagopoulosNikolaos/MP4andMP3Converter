import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Text
import threading
from Mp4_Converter import YouTubeDownloader
from Mp3_Converter import MP3Downloader
from pathlib import Path

class YouTubeDownloaderGUI:
    def __init__(self, master):
        """
        Initialize the GUI.
        
        Parameters
        ----------
        master : tkinter.Tk
            The root window of the GUI.
        
        Attributes
        ----------
        master : tkinter.Tk
            The root window of the GUI.
        downloader : YouTubeDownloader or MP3Downloader
            The downloader object. Initially set to None.
        default_download_path : str
            The default path where the downloaded files are saved. Set to the user's home directory.
        """
        
        self.master = master
        self.downloader = None  
        self.default_download_path = str(Path.home() / "Downloads")
        self.build_gui()

    def build_gui(self):
        """
        Builds the GUI for the YouTube downloader.
        
        This method creates all the widgets and layouts them in the root window.
        """
        
        self.master.title('MP4 Converter')
        tk.Label(self.master, text="Enter YouTube video URL:").grid(row=0, column=0, padx=10, pady=10)
        self.url_entry = tk.Entry(self.master, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_button = tk.Button(self.master, text="Browse Download Path", command=self.browse_path)
        self.browse_button.grid(row=1, column=0, padx=10, pady=10)

        self.path_display = tk.Entry(self.master, width=50)
        self.path_display.grid(row=1, column=1, padx=10, pady=10)

        self.download_button = tk.Button(self.master, text="Download!", command=self.start_download)
        self.download_button.grid(row=2, column=0, padx=10, pady=10)

        self.progress = ttk.Progressbar(self.master, orient='horizontal', length=300, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.close_button = tk.Button(self.master, text="Close", command=self.master.destroy)
        self.close_button.grid(row=4, column=0, padx=10, pady=10)

        self.format_var = tk.StringVar(value="MP4")
        tk.Label(self.master, text="Select download format:").grid(row=2, column=1, padx=10, pady=5)
        self.mp3_radio = tk.Radiobutton(self.master, text="MP3", variable=self.format_var, value="MP3")
        self.mp3_radio.grid(row=2, column=1, sticky='w', padx=12)
        self.mp4_radio = tk.Radiobutton(self.master, text="MP4", variable=self.format_var, value="MP4")
        self.mp4_radio.grid(row=2, column=1, sticky='e', padx=12)

        self.message_screen = Text(self.master, height=10, width=70)
        self.message_screen.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        self.message_screen.config(state=tk.DISABLED)

    def browse_path(self):
        """
        Opens a file dialog for the user to select a path to save the downloaded video/MP3.
        
        If a path is selected, the selected path is inserted into the path entry field.
        """
        path = filedialog.askdirectory()
        if path:
            self.path_display.delete(0, tk.END)
            self.path_display.insert(0, path)

    def start_download(self):
        """
        Starts the download process. 

        Retrieves the URL and path from the GUI fields and creates a YouTubeDownloader or MP3Downloader object.
        Sets the URL and path for the downloader object and starts a new thread to download the video or audio.
        Updates the GUI with a log message and resets the progress bar to 0.
        """
        self.progress['value'] = 0
        self.progress.update()

        url = self.url_entry.get()
        path = self.path_display.get() or self.default_download_path

        if self.format_var.get() == "MP4":
            self.downloader = YouTubeDownloader(self.update_progress)
            self.downloader.set_url(url)
            self.downloader.set_path(path)
            self.log_message("MP4 download started.")
            download_thread = threading.Thread(target=self.downloader.download_video)
        elif self.format_var.get() == "MP3":
            self.downloader = MP3Downloader(url, path, self.update_progress)
            self.log_message("MP3 download started.")
            download_thread = threading.Thread(target=self.downloader.download_as_mp3)
        download_thread.start()

    def update_progress(self, percentage):
        """
        Updates the progress bar in the GUI with the given percentage value.
        
        Parameters
        ----------
        percentage : int
            The percentage value to update the progress bar with.
        
        Notes
        -----
        If the percentage is 100, logs a message indicating download completion and clears the progress bar after 3 seconds.
        """
        self.progress['value'] = percentage
        self.progress.update()
        if percentage == 100:
            download_path = self.path_display.get() or self.default_download_path
            self.log_message(f"Download completed. File saved at {download_path}")
            self.master.after(3000, self.clear_progress_bar)


    def clear_progress_bar(self):
        """
        Resets the progress bar to 0.

        This method is called when a download is completed.
        """
        self.progress['value'] = 0
        self.progress.update()
    def log_message(self, message):
        self.message_screen.config(state=tk.NORMAL)
        self.message_screen.insert(tk.END, message + "\n")
        self.message_screen.see(tk.END)  # Auto-scroll to the bottom
        self.message_screen.config(state=tk.DISABLED)
def run_gui():
    """
    Starts the GUI for the YouTube downloader.

    Creates a new root window, creates a YouTubeDownloaderGUI object and starts the main event loop.
    """
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()

