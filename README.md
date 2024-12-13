# Music Conversion Script

A Python script to index and convert selected FLAC and M4A music files to MP3, offering options to select specific artists, calculate file sizes, and log the process.

---

## Features

- Converts `.flac` and `.m4a` files to `.mp3` using `ffmpeg`.
- Indexes music files and identifies artists from directory structure.
- Allows selective conversion by artist.
- Calculates file size savings post-conversion.
- Logs detailed progress and errors.
- Supports a dry-run mode for previewing changes.
- Archives converted files to another folder rather than delete

---

## Prerequisites

- Python 3.11 or higher.
- `ffmpeg` installed on your system.
- Virtual environment for package isolation (recommended)
