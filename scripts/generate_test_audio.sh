#!/bin/bash
# Generate a simple test MP3 file using ffmpeg if available
# Otherwise output instructions

if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg not installed. Install it and run:"
    echo "ffmpeg -f lavfi -i sine=frequency=440:duration=5 test_track.mp3"
    exit 1
fi

# Create a 5-second sine wave tone
ffmpeg -f lavfi -i sine=frequency=440:duration=5 -q:a 9 -acodec libmp3lame test_track.mp3
echo "Created test_track.mp3"
