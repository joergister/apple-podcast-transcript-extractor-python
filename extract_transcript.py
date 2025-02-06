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

def extract_text(element):
    """
    Recursively extracts all text from an XML element and its children.
    
    This function traverses an element and its child elements to gather the
    text content (including child text and tail texts).
    
    Args:
        element (xml.etree.ElementTree.Element): The XML element to search.
        
    Returns:
        str: The combined text from the element.
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
    Parses the content of a TTML file, extracts the included subtitle text
    (optionally with timestamps), and saves the result in a text file.
    
    The TTML content is parsed as XML. It searches for all <p> elements,
    which are usually located under <body>/<div>. From the <span> elements within a paragraph,
    the text is recursively extracted.
    If the flag include_timestamps is set and a paragraph has a "begin" attribute,
    that timestamp is formatted and prepended to the text.
    
    Args:
        ttml_content (str): The content of the TTML file as a string.
        output_path (str): The path where the transcript will be saved as a text file.
        include_timestamps (bool): Determines whether timestamps should be included in the transcript.
    """
    try:
        root = ET.fromstring(ttml_content)
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        return

    transcript = []

    # Search for all <p> elements within the TTML structure, which are typically
    # located under <body>/<div>. The XML namespace is ignored.
    paragraphs = root.findall(".//{*}body/{*}div/{*}p")
    for p in paragraphs:
        # Search for <span> elements in the paragraph to extract the text.
        span_elements = p.findall("{*}span")
        if span_elements:
            paragraph_text = ""
            for span in span_elements:
                # Recursively gather all text from the <span> and its children.
                paragraph_text += extract_text(span) + " "
            paragraph_text = paragraph_text.strip()
            if paragraph_text:
                # If timestamps are desired and a "begin" attribute is present,
                # format the timestamp and prepend it to the paragraph.
                if include_timestamps and 'begin' in p.attrib:
                    try:
                        seconds = float(p.attrib['begin'])
                    except ValueError:
                        seconds = 0
                    timestamp = format_timestamp(seconds)
                    transcript.append(f"[{timestamp}] {paragraph_text}")
                else:
                    transcript.append(paragraph_text)

    # Join the individual paragraphs with two newlines between them.
    output_text = "\n\n".join(transcript)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Transcript saved to {output_path}")
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")

def find_ttml_files(directory):
    """
    Recursively searches the specified directory for files with the ".ttml" extension.
    
    In each found file path, it checks if the string "PodcastContent" is present.
    The section immediately following that string is extracted as an ID, which is used
    for naming the output files.
    
    Args:
        directory (str): The base directory in which to search for TTML files.
        
    Returns:
        list: A list of dictionaries, each containing the full path ('path')
              and the extracted ID ('id').
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
    # For single file mode, two positional arguments can be provided:
    # input_file: Path to the TTML file, output_file: Path to the output text file.
    parser.add_argument("input_file", nargs="?", help="Input TTML file (single file mode)")
    parser.add_argument("output_file", nargs="?", help="Output text file (single file mode)")
    parser.add_argument("--timestamps", action="store_true", help="Include timestamps in the transcript")
    args = parser.parse_args()

    include_timestamps = args.timestamps

    # Create a "transcripts" directory to store the output files if it does not already exist.
    transcripts_dir = "./transcripts"
    if not os.path.exists(transcripts_dir):
        os.makedirs(transcripts_dir)

    # If both input_file and output_file are provided and the timestamp flag is not set,
    # single file mode is used.
    if args.input_file and args.output_file and not include_timestamps:
        try:
            with open(args.input_file, "r", encoding="utf-8") as f:
                ttml_content = f.read()
        except Exception as e:
            print(f"Error reading {args.input_file}: {e}")
            sys.exit(1)
        extract_transcript(ttml_content, args.output_file, include_timestamps)
    else:
        # Batch mode: Process all TTML files in a fixed directory.
        # The base directory is located in the current user's home directory.
        ttml_base_dir = os.path.join(
            os.path.expanduser("~"),
            "Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Library/Cache/Assets/TTML"
        )
        print("Searching for TTML files...")
        files = find_ttml_files(ttml_base_dir)
        print(f"Found {len(files)} TTML files")

        # To prevent output file name collisions, a counter is appended for duplicate IDs.
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
