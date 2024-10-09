import os
import subprocess
import argparse

def create_filelist_from_folder(folder_path, filelist_path='filelist.txt'):
    # Get all video files (assuming .mp4 files) from the folder
    video_files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
    
    # Sort video files to ensure they are merged in the correct order
    video_files.sort()

    # Create filelist.txt with full paths to each video file
    with open(filelist_path, 'w') as f:
        for video in video_files:
            full_path = os.path.join(folder_path, video)
            f.write(f"file '{full_path}'\n")

    return video_files

def get_total_duration(video_files):
    total_duration = 0
    for video in video_files:
        # Use FFmpeg to get the duration of each video file
        ffmpeg_command = [
            'ffmpeg', '-i', video, '-f', 'null', '/dev/null'
        ]
        
        result = subprocess.run(ffmpeg_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        
        # Parse the output to find the duration
        for line in result.stderr.splitlines():
            if "Duration" in line:
                # Extract the duration in hh:mm:ss.xx format
                duration_str = line.split("Duration: ")[1].split(",")[0]
                # Convert the duration to seconds
                h, m, s = map(float, duration_str.split(':'))
                total_duration += h * 3600 + m * 60 + s

    return total_duration

def merge_videos_from_folder(folder_path, output_file):
    # Step 1: Create the filelist.txt from all .mp4 files in the folder
    video_files = create_filelist_from_folder(folder_path)
    output_file = f"{folder_path}_{output_file}.mp4"

    if not video_files:
        print("No video files found in the folder.")
        return

    # Calculate total duration of the original videos
    total_duration = get_total_duration(video_files)
    print(f"Total duration of original videos: {total_duration // 3600}h {(total_duration % 3600) // 60}m {total_duration % 60:.2f}s")

    # Step 2: Run FFmpeg command to merge videos
    ffmpeg_command = [
        'ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'filelist.txt', '-c', 'copy', '-avoid_negative_ts', 'make_zero', output_file
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Successfully merged videos into {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error merging videos: {e}")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Merge videos from a folder.')
    parser.add_argument('--input', type=str, help='Path to the folder containing video files', required=True)
    parser.add_argument('--out', type=str, help='Name of the output merged video file', required=True)

    args = parser.parse_args()

    merge_videos_from_folder(args.input, args.out)
