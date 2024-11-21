# Music Conversion Script

A Python script to manage and convert FLAC and M4A music files to MP3, offering options to select specific artists, calculate file sizes, and log the process. The script includes a dry-run mode for safe testing without actual changes.

---

## Features

- Converts `.flac` and `.m4a` files to `.mp3` using `ffmpeg`.
- Indexes music files and identifies artists from directory structure.
- Allows selective conversion by artist.
- Calculates file size savings post-conversion.
- Logs detailed progress and errors.
- Supports a dry-run mode for previewing changes.

---

## Prerequisites

- Python 3.11 or higher.
- `ffmpeg` installed on your system.
- Virtual environment for package isolation (recommended).

---

## Setup Instructions