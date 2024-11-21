import os
import shutil
import subprocess
import json
from tqdm import tqdm
import logging
import argparse

# Setup logging
logging.basicConfig(filename='music_conversion.log', level=logging.INFO, format='%(asctime)s - %(message)s')
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
fh = logging.FileHandler('music_conversion_errors.log')
fh.setLevel(logging.ERROR)
error_logger.addHandler(fh)

# Directories
music_dir = '/Volumes/Media/Music'
flac_converted_dir = os.path.join(music_dir, 'FLAC_CONVERTED')
m4a_converted_dir = os.path.join(music_dir, 'M4A_CONVERTED')
index_file = 'music_index.json'

# Ensure conversion directories exist
os.makedirs(flac_converted_dir, exist_ok=True)
os.makedirs(m4a_converted_dir, exist_ok=True)

def index_music_files():
    flac_files = []
    m4a_files = []
    print("Indexing music files...")
    for root, _, files in os.walk(music_dir):
        # Skip converted directories
        if flac_converted_dir in root or m4a_converted_dir in root:
            continue
        print(f"Indexing: {root}", end='\r')  # Print the current folder being indexed
        for file in files:
            if file.endswith('.flac'):
                flac_files.append(os.path.join(root, file))
            elif file.endswith('.m4a'):
                m4a_files.append(os.path.join(root, file))
    print("\nIndexing complete.")
    with open(index_file, 'w') as f:
        json.dump({'flac': flac_files, 'm4a': m4a_files}, f)
    return flac_files, m4a_files

def load_index():
    with open(index_file, 'r') as f:
        data = json.load(f)
    return data['flac'], data['m4a']

def get_artists_with_files(files):
    artists = set()
    for file in files:
        parts = file.split(os.sep)
        if len(parts) > 5:  # Ensure we have enough parts to identify the artist level
            artist = parts[5]
            artists.add(artist)
    return list(artists)

def select_artists(artists, allow_all=False):
    print("Select artists to convert their files (comma separated):")
    print("0. None")
    if allow_all:
        print("all. All artists")
    for i, artist in enumerate(artists, 1):
        print(f"{i}. {artist}")
    choices = input("Enter numbers or 'all': ")
    if allow_all and choices.strip().lower() == 'all':
        return artists
    selected_indices = [int(num.strip()) - 1 for num in choices.split(',') if num.strip().isdigit()]
    selected_artists = [artists[i] for i in selected_indices if i >= 0]
    return selected_artists

def convert_file(input_file, output_file, dry_run=False):
    try:
        if dry_run:
            logging.info(f"[DRY RUN] Would convert {input_file} to {output_file}")
        else:
            subprocess.run(['ffmpeg', '-i', input_file, '-b:a', '320k', output_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        error_logger.error(f"Error converting {input_file}: {e}")
        return False
    return True

def calculate_size(file):
    return os.path.getsize(file)

def process_files(files, convert_artists, converted_dir, dry_run=False):
    total_original_size = 0
    total_converted_size = 0
    for file in tqdm(files, desc="Processing files", unit="file"):
        parts = file.split(os.sep)
        if len(parts) > 5:
            artist = parts[5]
            if artist in convert_artists:
                output_file = file.replace('.flac', '.mp3').replace('.m4a', '.mp3')
                original_size = calculate_size(file)
                total_original_size += original_size
                if convert_file(file, output_file, dry_run):
                    new_path = os.path.join(converted_dir, os.path.relpath(file, music_dir))
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    if dry_run:
                        logging.info(f"[DRY RUN] Would move {file} to {new_path}")
                    else:
                        shutil.move(file, new_path)
                        converted_size = calculate_size(output_file)
                        total_converted_size += converted_size
                    logging.info(f"{'Converted' if not dry_run else '[DRY RUN] Converted'} {file} to {output_file}")
                else:
                    logging.error(f"{'Failed to convert' if not dry_run else '[DRY RUN] Failed to convert'} {file}")
    
    if not dry_run:
        space_saved = total_original_size - total_converted_size
        print(f"Total original size: {total_original_size / (1024*1024):.2f} MB")
        print(f"Total converted size: {total_converted_size / (1024*1024):.2f} MB")
        print(f"Space saved: {space_saved / (1024*1024):.2f} MB")
        logging.info(f"Total original size: {total_original_size} bytes")
        logging.info(f"Total converted size: {total_converted_size} bytes")
        logging.info(f"Space saved: {space_saved} bytes")

def main(dry_run=False):
    if os.path.exists(index_file):
        refresh_index = input("Index file found. Refresh index? (y/n): ").strip().lower()
        if refresh_index == 'y':
            flac_files, m4a_files = index_music_files()
        else:
            flac_files, m4a_files = load_index()
    else:
        flac_files, m4a_files = index_music_files()

    logging.info(f"Found {len(flac_files)} FLAC files and {len(m4a_files)} M4A files.")

    flac_artists = get_artists_with_files(flac_files)
    m4a_artists = get_artists_with_files(m4a_files)

    print("Artists with FLAC files:")
    convert_flac_artists = select_artists(flac_artists)
    if convert_flac_artists:
        logging.info(f"Converting FLAC for artists: {', '.join(convert_flac_artists)}")
        process_files(flac_files, convert_flac_artists, flac_converted_dir, dry_run)
    else:
        logging.info("No artists selected for FLAC conversion.")

    print("Artists with M4A files:")
    convert_m4a_artists = select_artists(m4a_artists, allow_all=True)
    if convert_m4a_artists:
        logging.info(f"Converting M4A for artists: {', '.join(convert_m4a_artists)}")
        process_files(m4a_files, convert_m4a_artists, m4a_converted_dir, dry_run)
    else:
        logging.info("No artists selected for M4A conversion.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Music file conversion script with dry run feature.')
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without making any changes.')
    args = parser.parse_args()

    main(dry_run=args.dry_run)
