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
