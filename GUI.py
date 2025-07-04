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
        self.master.title('MP4 Converter')
        tk.Label(self.master, text="Enter YouTube video URL:").grid(row=0, column=0, padx=10, pady=10)
        self.url_entry = tk.Entry(self.master, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        # The fetch button is now removed, as fetching is automatic.

        self.browse_button = tk.Button(self.master, text="Browse Download Path", command=self.browse_path)
        self.browse_button.grid(row=1, column=0, padx=10, pady=10)

        self.path_display = tk.Entry(self.master, width=50)
        self.path_display.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.master, text="Resolution:").grid(row=1, column=2, padx=10, pady=10, sticky='w')
        self.resolution_var = tk.StringVar(self.master)
        self.resolution_menu = tk.OptionMenu(self.master, self.resolution_var, "")
        self.resolution_menu.grid(row=1, column=2, padx=80, pady=10, sticky='e')


        self.download_button = tk.Button(self.master, text="Download!", command=self.start_download)
        self.download_button.grid(row=2, column=0, padx=10, pady=10)

        self.progress = ttk.Progressbar(self.master, orient='horizontal', length=300, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.close_button = tk.Button(self.master, text="Close", command=self.master.destroy)
        self.close_button.grid(row=4, column=0, padx=10, pady=10)

        self.format_var = tk.StringVar(value="MP4")
        tk.Label(self.master, text="Select download format:").grid(row=2, column=1, padx=10, pady=5)
        self.mp3_radio = tk.Radiobutton(self.master, text="MP3", variable=self.format_var, value="MP3", command=self.update_format_color)
        self.mp3_radio.grid(row=2, column=1, sticky='w', padx=12)
        self.mp4_radio = tk.Radiobutton(self.master, text="MP4", variable=self.format_var, value="MP4", command=self.update_format_color)
        self.mp4_radio.grid(row=2, column=1, sticky='e', padx=12)

        self.message_screen = Text(self.master, height=10, width=70)
        self.message_screen.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
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
            self.url_entry.config(bg="red")
            self.path_display.config(bg="red")
        elif self.format_var.get() == "MP3":
            self.downloader = MP3Downloader(url, path, self.update_progress, self.log_message)
            download_thread = threading.Thread(target=self.downloader.download_as_mp3)
            self.url_entry.config(bg="blue")
            self.path_display.config(bg="blue")
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
        if self.format_var.get() == "MP4":
            self.mp4_radio.config(fg="red")
            self.mp3_radio.config(fg="black")
        else:
            self.mp3_radio.config(fg="red")
            self.mp4_radio.config(fg="black")

def run_gui():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
