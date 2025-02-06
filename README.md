# Apple Podcast Transcript Extractor (Python)

A Python tool for extracting transcripts from TTML files used in Apple Podcasts. This script parses TTML files to extract subtitle text—optionally including timestamps—and saves the transcript as a plain text file. Inspired by https://github.com/mattdanielmurphy/apple-podcast-transcript-extractor

## Why This Project Exists

Copying transcripts from Apple Podcasts is tedious due to selection restrictions. However, when a transcript is viewed or an episode is downloaded, it is cached in a specific folder in a machine-readable format. This script extracts and converts these transcripts into a human-readable format, enabling storage in vector Databases and semantic search.

## Features

- **Single File Mode:** Extracts a transcript from a specified TTML file and saves it as a text file.
- **Batch Mode:** Searches for and extracts transcripts from TTML files stored in Apple Podcasts' cache directory:
  
  ```bash
  Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Library/Cache/Assets/TTML
  ```
- **Timestamp Support:** Optionally includes formatted timestamps (HH:MM:SS) for each transcript segment based on the `begin` attribute in the TTML file.

## Requirements

- Python 3.6 or later
- Uses built-in Python libraries: `os`, `sys`, `re`, `xml.etree.ElementTree`, and `argparse` (no additional dependencies required).

## Usage

### Single File Mode
Extract a transcript from a single TTML file:

```bash
python extract_transcript.py input.ttml output.txt
```

*Note: The `--timestamps` flag is ignored in single file mode.*

### Batch Mode
Automatically extract transcripts from all TTML files in the default directory:

```bash
python extract_transcript.py --timestamps
```

All output files are saved in the `./transcripts` folder, which is created automatically if it does not exist.

## How It Works

### Parsing TTML Files
The script uses Python’s XML parser (`xml.etree.ElementTree`) to extract `<p>` elements under `<body>/<div>`, gathering text from `<span>` elements within each paragraph.

### Timestamp Formatting
If the `--timestamps` flag is used, timestamps are extracted from the `begin` attribute and formatted as `HH:MM:SS`, then prepended to the transcript segment.

### File Naming
In batch mode, filenames are derived from the occurrence of "PodcastContent" in the file path. If multiple files share the same identifier, a counter is appended to avoid name collisions.

## Example

Extract a transcript from a specific file:

```bash
python extract_transcript.py episode123.ttml transcript_episode123.txt
```

Process all TTML files in the default directory with timestamps:

```bash
python extract_transcript.py --timestamps
```

