# Speech to Text Converter

A simple desktop application that converts speech to text using OpenAI's Whisper API.

## Features

- Simple and intuitive Tkinter-based UI
- Support for various audio formats (MP3, WAV, MP4, M4A, WEBM)
- Copy transcription to clipboard
- Save transcription as a text file
- Status bar updates

## Requirements

- Python 3.6 or higher
- OpenAI API key

## Installation

### Using UV (Recommended)

1. Clone this repository or download the files
2. Make sure you have UV installed:
   ```
   pip install uv
   ```
3. Install the application with UV:
   ```
   uv pip install -e .
   ```

### Using Pip

1. Clone this repository or download the files
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### API Key Setup

Create a `.env` file in the project directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

1. Run the application:
   ```
   python run.py
   ```
   
   Or if installed with UV:
   ```
   python -m speech_to_text
   ```

2. Click the "Browse" button to select an audio file
3. Click the "Transcribe" button to start the transcription process
4. Wait for the transcription to complete
5. Use the "Copy to Clipboard" or "Save as Text File" buttons to save the transcription

## Development

This project uses `pyproject.toml` for dependency management. To install development dependencies:

```
uv pip install -e ".[dev]"
```

## Notes

- The transcription process may take some time depending on the length of the audio file
- The application uses the "whisper-1" model from OpenAI
- Make sure you have a valid OpenAI API key with sufficient credits
