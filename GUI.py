# GUI.py

# imports
# At the top of your GUI.py file, add the moviepy import statement
from moviepy.editor import VideoFileClip, AudioFileClip
from Time_cuts import MediaFile
import tkinter as tk
from tkinter import ttk, filedialog, OptionMenu
from tkinter import simpledialog, messagebox
from Mp4_Converter import YouTubeDownloader
from Mp3_Converter import MP3Downloader  # Adjust the import statement as necessary
import threading
from pytube import YouTube
from pytube.cli import on_progress


class YouTubeDownloaderGUI:
    """
        YouTubeDownloaderGUI class is responsible for creating a graphical user interface for downloading YouTube videos and converting them to MP3 format.

        Attributes:
            master (tkinter.Tk): The root window of the GUI.
            downloader (YouTubeDownloader): An instance of the YouTubeDownloader class for downloading videos.
            media_file (MediaFile): An instance of the MediaFile class for manipulating media files.

        Methods:
            __init__(self, master):
                Initializes a new instance of the YouTubeDownloaderGUI class.
                
                Parameters:
                    master (tkinter.Tk): The root window of the GUI.
                
                Returns:
                    None
            
            build_gui(self):
                Builds the graphical user interface for the YouTubeDownloaderGUI class.
                
                Returns:
                    None
            
            browse_path(self):
                Opens a file dialog to browse and select a download path.
                
                Returns:
                    None
            
            start_download(self):
                Starts the download process for the selected YouTube video.
                
                Returns:
                    None
            
            update_progress(self, percentage):
                Updates the progress bar with the given percentage value.
                
                Parameters:
                    percentage (int): The percentage value to update the progress bar.
                
                Returns:
                    None
            
            set_url(self, url):
                Sets the URL for the video to be downloaded.
                
                Parameters:
                    url (str): The URL of the YouTube video.
                
                Returns:
                    None
            
            set_path(self, save_path):
                Sets the path where the downloaded MP3 file will be saved.
                
                Parameters:
                    save_path (str): The path where the MP3 file will be saved.
                
                Returns:
                    None
            
            browse_media(self):
                Opens a file dialog to browse and select a media file.
                
                Returns:
                    None
            
            update_cut_progress(self, value):
                Updates the progress bar for the media cutting process with the given value.
                
                Parameters:
                    value (int): The value to update the progress bar.
                
                Returns:
                    None
            
            cut_media(self):
                Cuts the selected media file based on the provided start and end times and saves the output to the specified path.
                
                Returns:
                    None
    """
    def __init__(self, master):
        """
        Initialize the class with the given master widget.
        
        :param master: The master widget to initialize the class with.
        """
        
        self.master = master
        self.downloader = YouTubeDownloader(self.update_progress)
        self.downloader = MP3Downloader(None, None)  # Initialize with placeholders
        self.media_file = None
        self.build_gui()


    def build_gui(self):
        """
        Function to build the GUI for the MP4 Converter application.
        """
        
        
        self.master.title('MP4 Converter')

        # URL Entry
        tk.Label(self.master, text="Enter YouTube video URL:").grid(row=0, column=0, padx=10, pady=10)
        self.url_entry = tk.Entry(self.master, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        # Browse Button
        self.browse_button = tk.Button(self.master, text="Browse Download Path", command=self.browse_path)
        self.browse_button.grid(row=1, column=0, padx=10, pady=10)

        # Path Display
        self.path_display = tk.Entry(self.master, width=50)
        self.path_display.grid(row=1, column=1, padx=10, pady=10)

        # Download Button
        self.download_button = tk.Button(self.master, text="Download!", command=self.start_download)
        self.download_button.grid(row=2, column=0,  padx=10, pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.master, orient='horizontal', length=300, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Close Button
        self.close_button = tk.Button(self.master, text="__Close__", command=self.master.destroy)
        self.close_button.grid(row=4, column=0, padx=10, pady=10)
        # Format Selection
        self.format_var = tk.StringVar(value="MP4")
        tk.Label(self.master, text="Select download format:").grid(row=2, column=1, padx=10, pady=5)
        self.mp3_radio = tk.Radiobutton(self.master, text="MP3", variable=self.format_var, value="MP3")
        self.mp3_radio.grid(row=2, column=1, sticky='w', padx=12)
        self.mp4_radio = tk.Radiobutton(self.master, text="MP4", variable=self.format_var, value="MP4")
        self.mp4_radio.grid(row=2, column=1, sticky='e', padx=12)

        # Add a separator for better visual organization
        ttk.Separator(self.master, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=20)

        
        # Media Cutter Section
        ttk.Separator(self.master, orient='horizontal').grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=20)

        tk.Label(self.master, text="Select Media File:").grid(row=7, column=0, padx=10, pady=10)
        self.media_select_button = tk.Button(self.master, text="Browse Media File", command=self.browse_media)
        self.media_select_button.grid(row=7, column=1, padx=10, pady=10)

        tk.Label(self.master, text="Start Time (s):").grid(row=8, column=0, padx=10, pady=10)
        self.start_time_entry = tk.Entry(self.master)
        self.start_time_entry.grid(row=8, column=1, padx=10, pady=10)

        tk.Label(self.master, text="End Time (s):").grid(row=9, column=0, padx=10, pady=10)
        self.end_time_entry = tk.Entry(self.master)
        self.end_time_entry.grid(row=9, column=1, padx=10, pady=10)

        self.cut_button = tk.Button(self.master, text="Cut Media", command=self.cut_media)
        self.cut_button.grid(row=10, column=0, columnspan=2, padx=10, pady=10)

        # Progress Bar for Media Cutting
        self.cut_progress = ttk.Progressbar(self.master, orient='horizontal', length=300, mode='determinate')
        self.cut_progress.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

        
        
            
    def browse_path(self):
        """
        Function to browse and select a directory path using a file dialog.
        """
        
        
        path = filedialog.askdirectory()
        if path:
            self.path_display.delete(0, tk.END)
            self.path_display.insert(0, path)

    def start_download(self):
        """
        Starts the download process.

        This function initializes the progress bar to 0 and updates it. It then retrieves the URL and path from the respective entry fields. Based on the selected format, it determines which downloader to use. If the selected format is "MP4", it creates an instance of the YouTubeDownloader class and sets the URL and path. It then starts a new thread to download the video using the download_video method of the YouTubeDownloader instance. If the selected format is "MP3", it creates an instance of the MP3Downloader class with the URL and path. It starts a new thread to download the video as MP3 using the download_as_mp3 method of the MP3Downloader instance.

        Parameters:
            self (object): The instance of the class.

        Returns:
            None
        """
        self.progress['value'] = 0
        self.progress.update()

        url = self.url_entry.get()
        path = self.path_display.get()

        # Decide which downloader to use based on the selected format
        if self.format_var.get() == "MP4":
            self.downloader = YouTubeDownloader(self.update_progress)  # Ensure this is the correct class for MP4 downloads
            self.downloader.set_url(url)
            self.downloader.set_path(path)
            download_thread = threading.Thread(target=self.downloader.download_video)
        elif self.format_var.get() == "MP3":
            self.downloader = MP3Downloader(url, path)  # Adjust the constructor as necessary
            download_thread = threading.Thread(target=self.downloader.download_as_mp3)  # Ensure this method exists in MP3Downloader

        download_thread.start()


    def update_progress(self, percentage):
        """
        Update the progress value in the GUI based on the given percentage.

        Parameters:
            percentage (int): The percentage value to update the progress bar to.
        """
        
        self.progress['value'] = percentage
        self.progress.update()
        
    def set_url(self, url):
        """
    	  Set the URL for the object.
    	
    	 :param url: The URL to be set
        """
    
        self.url = url

    def set_path(self, save_path):
        """
        Sets the save path for the object.

        Parameters:
            save_path (str): The path where the object will be saved.

        Returns:
            None
        """
        
        self.save_path = save_path

    def browse_media(self):
        """
        Allow user to select a media file.
        """
        
        file_path = filedialog.askopenfilename(filetypes=[("MP4 Files", "*.mp4"), ("MP3 Files", "*.mp3")])
        if file_path:
            self.media_file_path = file_path
            messagebox.showinfo("File Selected", "File selected successfully.")

    def update_cut_progress(self, value):
        """
        Update the cut progress value.

        Parameters:
            value (any): The new value for the cut progress.

        Returns:
            None
        """
        self.cut_progress['value'] = value
        self.master.update_idletasks()  # Refresh GUI

    def cut_media(self):
        """
        A function to cut a media file based on the start and end time provided by the user.
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            start_time = float(self.start_time_entry.get())
            end_time = float(self.end_time_entry.get())
            
            # Define initial file name and format based on the input file's extension
            default_file_name = "output"
            file_extension = ".mp4" if self.media_file_path.endswith(".mp4") else ".mp3"
            initial_file = default_file_name + file_extension

            # Ask the user for the output file location, providing a default file name and extension
            output_path = filedialog.asksaveasfilename(
                initialfile=initial_file,
                defaultextension=file_extension,
                filetypes=[("MP4 files", "*.mp4"), ("MP3 files", "*.mp3")]
            )
            
            if not output_path:  # User cancelled the operation
                return
            
            self.cut_progress['value'] = 0
            self.master.update_idletasks()  # Update the GUI to reflect the progress reset immediately

            media_file = MediaFile(self.media_file_path)
            media_file.cut_by_seconds(start_time, end_time, output_path, self.update_cut_progress)

            messagebox.showinfo("Success", "Media cut successfully.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input for start or end time. Please enter a valid number.")


    
# This is how you would run the GUI from the separate file.
def run_gui():
    """
    Runs the GUI for the YouTube downloader.

    This function creates a Tkinter root window and initializes an instance of the
    YouTubeDownloaderGUI class. It then enters the main event loop, allowing
    the user to interact with the GUI.

    Parameters:
        None

    Returns:
        None
    """
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    
    root.mainloop()


if __name__ == "__main__":
    run_gui()


#pip install auto-py-to-exe
#auto-py-to-exe