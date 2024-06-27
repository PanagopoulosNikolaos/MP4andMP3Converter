from moviepy.editor import VideoFileClip, AudioFileClip
import time
class MediaFile:
    
    """
        A class representing a media file.

        Attributes:
            file_path (str): The path to the media file.
            clip (VideoFileClip or AudioFileClip): The video or audio clip loaded from the file.

        Methods:
            __init__(file_path):
                Initializes a new instance of the class with the given file path.
                
            get_duration():
                Returns the duration of the media clip.
                
            cut_by_seconds(start, end, output_path, progress_callback=None):
                Cuts the media file by the given start and end times and saves the output to the specified output path.
    """
    
    def __init__(self, file_path):
        """
        Initializes a new instance of the class with the given file path.

        Parameters:
            file_path (str): The path to the file to be loaded.

        Raises:
            ValueError: If the file format is not supported.

        Returns:
            None
        """
        self.file_path = file_path
        if file_path.endswith('.mp4'):
            self.clip = VideoFileClip(file_path)
        elif file_path.endswith('.mp3'):
            self.clip = AudioFileClip(file_path)
        else:
            raise ValueError("Unsupported file format")

    def get_duration(self):
        """
        A method to get the duration of the video clip.
        No parameters.
        Returns the duration of the video clip.
        """
        return self.clip.duration

    def cut_by_seconds(self, start, end, output_path, progress_callback=None):
        """
        Cuts a video or audio file by the given start and end times and saves the output to the specified output path.

        Args:
            start (float): The starting time of the cut in seconds.
            end (float): The ending time of the cut in seconds.
            output_path (str): The path where the output file will be saved.
            progress_callback (function, optional): A callback function that will be called to indicate the progress of the cutting process. This function takes a single argument, which is the current progress percentage. Defaults to None.

        Returns:
            None
        """
        cut_clip = self.clip.subclip(start, end)
        # Simulate progress
        total_steps = 10
        for step in range(total_steps):
            if progress_callback:
                progress_callback((step + 1) * 10)  # Update progress
            time.sleep(0.1)  # Simulated delay for demonstration
        if self.file_path.endswith('.mp4'):
            cut_clip.write_videofile(output_path)
        elif self.file_path.endswith('.mp3'):
            cut_clip.write_audiofile(output_path)

          




