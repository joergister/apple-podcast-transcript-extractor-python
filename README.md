# Apple Podcast Transcript Extractor (Python)

A Python tool for extracting transcripts from TTML files, typically used in Apple Podcasts. This script parses TTML files to extract subtitle text—optionally including timestamps—and saves the transcript as a plain text file. Inspired by https://github.com/mattdanielmurphy/apple-podcast-transcript-extractor

## Why This Project Exists

Existing tools do not allow for effective semantic search across transcripts of various podcast episodes.
Apple Podcasts generates transcripts for most podcasts, but copying them is tedious due to restrictions on how much text can be selected at once. However, if an episode’s transcript is viewed or the episode is downloaded, the app caches the transcript in a specific folder in a machine-readable format.

This script extracts those cached transcripts, making them easily accessible and converting them into a human-readable format. This enables efficient storage in vector databases and allows for semantic searching.

## Features

## Features

- **Single File Mode:** Extract a transcript from a specified TTML file and save it to an output text file.
- **Batch Mode:** Automatically searches for TTML files in the directory that the apple podcasts app stores them in 

```bash
Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Library/Cache/Assets/TTML
```
and extracts transcripts for all of them.
- **Timestamp Support:** Optionally include formatted timestamps (HH:MM:SS) for each transcript segment based on the `begin` attribute in the TTML file.

## Requirements

- Python 3.6 or later
- No additional packages are required, as the script uses Python’s built-in libraries (`os`, `sys`, `re`, `xml.etree.ElementTree`, and `argparse`).

## Usage

The script supports two modes:

### Single File Mode
Process a single TTML file and save the transcript to a specified output text file.

```bash
python extract_transcript.py input.ttml output.txt
```

*Note: In single file mode, the `--timestamps` flag is ignored. Use batch mode to include timestamps.*

### Batch Mode
Automatically search for TTML files in the default directory and extract transcripts for all of them. The default directory is:

```swift
~/Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Library/Cache/Assets/TTML
```

Run the script without specifying input/output files. Optionally, include timestamps by adding the `--timestamps` flag:

```bash
python extract_transcript.py --timestamps
```

All output transcript files will be saved in the `./transcripts` folder. If the folder does not exist, it will be created automatically.

## How It Works

### Parsing TTML Files
The script uses Python's built-in XML parser (`xml.etree.ElementTree`) to parse the TTML file. It extracts `<p>` elements located under `<body>/<div>`, then recursively gathers text from the `<span>` elements within each paragraph.

### Timestamp Formatting
If a paragraph includes a `begin` attribute and the `--timestamps` flag is provided, the script converts the value (in seconds) to a formatted string (`HH:MM:SS`) and prepends it to the transcript segment.

### File Naming
In batch mode, the script recursively searches for TTML files in the designated folder. It extracts an identifier from the file path (based on the occurrence of "PodcastContent") and uses it to name the output transcript files. If multiple files share the same identifier, a counter is appended to avoid file name collisions.

### Example
Assuming you have a TTML file named `episode123.ttml` in the current directory, you can extract its transcript with:

```bash
python extract_transcript.py episode123.ttml transcript_episode123.txt
```

To process all TTML files in the default directory with timestamps included:

```bash
python extract_transcript.py --timestamps
```

