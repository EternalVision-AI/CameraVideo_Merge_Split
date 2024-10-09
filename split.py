import os
import subprocess
from datetime import datetime, timedelta
def get_start_time_from_filename(input_file):
    """
    Extracts the start time from a video file name in the format "DDMMYY_HHMMSS.mp4".

    :param input_file: Input video file name (e.g., "240816_000059.mp4")
    :return: A datetime object representing the start time.
    """
    # Remove the file extension and split the name into date and time parts
    filename = input_file.split('.')[0]
    date_part, time_part = filename.split('_')

    # Parse the date and time parts
    day = int(date_part[:2])
    month = int(date_part[2:4])
    year = int("20" + date_part[4:])  # Assuming the year is in "YY" format, e.g., "21" -> "2021"
    hour = int(time_part[:2])
    minute = int(time_part[2:4])
    second = int(time_part[4:])

    # Create a datetime object
    start_time = datetime(year, month, day, hour, minute, second)
    
    return start_time
def split_video(input_file, start_time, duration="01:00:00"):
    """
    Splits a video into multiple segments, each with a specified duration, and names the output files according to a custom pattern.

    :param input_file: Path to the input video file (e.g., "video.mp4")
    :param start_time: A datetime object representing the start time of the first segment.
    :param duration: Duration of each split segment (default is 1 hour).
    """
    try:
        # Convert duration to seconds for easier calculation
        duration_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], duration.split(":")))

        # Extract total duration of the video using ffprobe
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
        total_duration = float(subprocess.check_output(cmd).strip())

        segment_count = int(total_duration // duration_seconds) + 1

        for i in range(segment_count):
            # Calculate the timestamp for each segment
            segment_start_time = start_time + timedelta(seconds=i * duration_seconds)
            
            # Generate the output filename based on your required pattern: "DDMMYY_HHMMSS"
            output_filename = "view1_2024" + segment_start_time.strftime('-%m-%y_%H-%M-%S') + ".mp4"
            
            # Build ffmpeg command to split the video
            command = [
                'ffmpeg', '-i', input_file,
                '-c', 'copy',  # Copy codec without re-encoding
                '-map', '0',  # Map all streams from input
                '-ss', str(timedelta(seconds=i * duration_seconds)),  # Start time for the segment
                '-t', duration,  # Duration of the segment
                output_filename
            ]
            
            # Run the ffmpeg command
            subprocess.run(command, check=True)
            print(f"Created segment: {output_filename}")

    except subprocess.CalledProcessError as e:
        print(f"Error splitting video: {e}")
if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Merge videos from a folder.')
    parser.add_argument('--input', type=str, help='Path to the folder containing video files', required=True)

    args = parser.parse_args()
    # Example usage
    input_file = f"{args.input}.mp4"  # Input video file
    start_time = get_start_time_from_filename(f"{args.input}_000000.mp4")
    print(start_time)
    split_video(input_file, start_time)

