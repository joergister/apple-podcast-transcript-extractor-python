#!/usr/bin/env python3
import os
import sys
import re
import xml.etree.ElementTree as ET
import argparse

def format_timestamp(seconds):
    """
    Converts a time in seconds to the format HH:MM:SS.
    
    Args:
        seconds (float): Time in seconds.
        
    Returns:
        str: Time in the format "HH:MM:SS".
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def parse_timecode(time_str):
    """
    Parses a timecode in the format H:MM:SS(.mmm) or M:SS(.mmm)
    and returns the total number of seconds.
    
    Args:
        time_str (str): Timecode string, e.g. "1:40:14.700" or "40:15.800"
    
    Returns:
        float: Total seconds represented by the timecode.
    """
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            # Format: H:MM:SS(.mmm)
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            # Format: M:SS(.mmm)
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        else:
            # If no colon is found, assume it's just seconds.
            return float(time_str)
    except ValueError:
        return 0

def extract_text(element):
    """
    Recursively extracts all text from an XML element and its children.
    
    Args:
        element (xml.etree.ElementTree.Element): The XML element.
        
    Returns:
        str: Combined text content.
    """
    texts = []
    if element.text:
        texts.append(element.text)
    for child in element:
        texts.append(extract_text(child))
        if child.tail:
            texts.append(child.tail)
    return " ".join(texts).strip()

def extract_transcript(ttml_content, output_path, include_timestamps=False):
    """
    Parses the TTML content, extracts subtitle text (with optional timestamps),
    and saves the transcript to a text file.
    
    This version mimics the JavaScript code by navigating to:
      tt -> body -> div -> p
    and then processing each <p> element.
    
    Args:
        ttml_content (str): The TTML file content.
        output_path (str): Path to save the transcript.
        include_timestamps (bool): Whether to include timestamps.
    """
    try:
        root = ET.fromstring(ttml_content)
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        return

    transcript = []

    # Navigate to <tt><body><div>
    body = root.find('.//{*}body')
    if body is None:
        print("No <body> element found in TTML.")
        return
    div = body.find('{*}div')
    if div is None:
        print("No <div> element found in TTML.")
        return

    paragraphs = div.findall('{*}p')
    for p in paragraphs:
        # Only process paragraphs that contain <span> elements.
        span_elements = p.findall('{*}span')
        if not span_elements:
            continue

        paragraph_text = ""
        for span in span_elements:
            # Recursively extract text from each span.
            paragraph_text += extract_text(span) + " "
        paragraph_text = paragraph_text.strip()

        if paragraph_text:
            if include_timestamps and 'begin' in p.attrib:
                begin_time_str = p.attrib['begin'].strip()
                seconds = parse_timecode(begin_time_str)
                timestamp = format_timestamp(seconds)
                transcript.append(f"[{timestamp}] {paragraph_text}")
            else:
                transcript.append(paragraph_text)

    output_text = "\n\n".join(transcript)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Transcript saved to {output_path}")
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")

def find_ttml_files(directory):
    """
    Recursively finds TTML files in a directory.
    
    Args:
        directory (str): Base directory to search.
        
    Returns:
        list: List of dictionaries with 'path' and extracted 'id' for each TTML file.
    """
    ttml_files = []
    for root_dir, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".ttml"):
                full_path = os.path.join(root_dir, file)
                match = re.search(r'PodcastContent([^/\\]+)', full_path)
                if match:
                    file_id = match.group(1)
                    ttml_files.append({'path': full_path, 'id': file_id})
    return ttml_files

def main():
    parser = argparse.ArgumentParser(
        description="Extracts subtitles from TTML files and saves them as text files."
    )
    parser.add_argument("input_file", nargs="?", help="Input TTML file (single file mode)")
    parser.add_argument("output_file", nargs="?", help="Output text file (single file mode)")
    parser.add_argument("--timestamps", action="store_true", help="Include timestamps in the transcript")
    args = parser.parse_args()

    include_timestamps = args.timestamps

    # Create an output directory for transcripts.
    transcripts_dir = "./transcripts"
    if not os.path.exists(transcripts_dir):
        os.makedirs(transcripts_dir)

    if args.input_file and args.output_file:
        # Single file mode.
        try:
            with open(args.input_file, "r", encoding="utf-8") as f:
                ttml_content = f.read()
        except Exception as e:
            print(f"Error reading {args.input_file}: {e}")
            sys.exit(1)
        extract_transcript(ttml_content, args.output_file, include_timestamps)
    else:
        # Batch mode: process all TTML files in a fixed directory.
        ttml_base_dir = os.path.join(
            os.path.expanduser("~"),
            "Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Library/Cache/Assets/TTML"
        )
        print("Searching for TTML files...")
        files = find_ttml_files(ttml_base_dir)
        print(f"Found {len(files)} TTML files")

        # To avoid filename collisions.
        filename_counts = {}
        for file in files:
            base_filename = file['id']
            count = filename_counts.get(base_filename, 0)
            suffix = "" if count == 0 else f"-{count}"
            output_path = os.path.join(transcripts_dir, f"{base_filename}{suffix}.txt")
            filename_counts[base_filename] = count + 1

            try:
                with open(file['path'], "r", encoding="utf-8") as f:
                    ttml_content = f.read()
            except Exception as e:
                print(f"Error reading {file['path']}: {e}")
                continue
            extract_transcript(ttml_content, output_path, include_timestamps)

if __name__ == "__main__":
    main()
