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

# Default directories
config_file = 'music_conversion_config.json'
default_music_dir = '/Volumes/Media/Music'
default_flac_dir = 'FLAC_CONVERTED'
default_m4a_dir = 'M4A_CONVERTED'
default_index_file = 'music_index.json'

# Load or set directories
def get_directories():
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        music_dir = config.get('music_dir', default_music_dir)
        flac_dir = config.get('flac_dir', default_flac_dir)
        m4a_dir = config.get('m4a_dir', default_m4a_dir)
    else:
        music_dir = input(f"Folder to scan [{default_music_dir}]: ").strip() or default_music_dir
        flac_dir = input(f"Folder to store converted FLACs [{default_flac_dir}]: ").strip() or default_flac_dir
        m4a_dir = input(f"Folder to store converted M4As [{default_m4a_dir}]: ").strip() or default_m4a_dir

        save_config = input("Save these settings for future runs? (y/n): ").strip().lower()
        if save_config == 'y':
            with open(config_file, 'w') as f:
                json.dump({'music_dir': music_dir, 'flac_dir': flac_dir, 'm4a_dir': m4a_dir}, f)

    flac_converted_dir = os.path.join(music_dir, flac_dir)
    m4a_converted_dir = os.path.join(music_dir, m4a_dir)

    os.makedirs(flac_converted_dir, exist_ok=True)
    os.makedirs(m4a_converted_dir, exist_ok=True)

    return music_dir, flac_converted_dir, m4a_converted_dir

def index_music_files(music_dir, index_file):
    flac_files = []
    m4a_files = []
    print("Indexing music files...")
    for root, _, files in os.walk(music_dir):
        if flac_converted_dir in root or m4a_converted_dir in root:
            continue
        print(f"Indexing: {root}", end='\r')
        for file in files:
            if file.endswith('.flac'):
                flac_files.append(os.path.join(root, file))
            elif file.endswith('.m4a'):
                m4a_files.append(os.path.join(root, file))
    print("\nIndexing complete.")
    with open(index_file, 'w') as f:
        json.dump({'flac': flac_files, 'm4a': m4a_files}, f)
    return flac_files, m4a_files

def load_index(index_file):
    with open(index_file, 'r') as f:
        data = json.load(f)
    return data['flac'], data['m4a']

def main(dry_run=False):
    music_dir, flac_converted_dir, m4a_converted_dir = get_directories()
    index_file = os.path.join(music_dir, default_index_file)

    if os.path.exists(index_file):
        refresh_index = input("Index file found. Refresh index? (y/n): ").strip().lower()
        if refresh_index == 'y':
            flac_files, m4a_files = index_music_files(music_dir, index_file)
        else:
            flac_files, m4a_files = load_index(index_file)
    else:
        flac_files, m4a_files = index_music_files(music_dir, index_file)

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
    parser = argparse.ArgumentParser(description='Music file conversion script with directory settings.')
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without making any changes.')
    args = parser.parse_args()

    main(dry_run=args.dry_run)