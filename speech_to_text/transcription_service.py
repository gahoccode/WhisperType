"""
Transcription service for the Speech to Text application.
Handles communication with the OpenAI API for audio transcription.
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

class TranscriptionService:
    """Handles audio transcription using OpenAI's Whisper API."""
    
    def __init__(self):
        """Initialize the transcription service."""
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client - it will automatically use OPENAI_API_KEY from env
        self.client = OpenAI()
        
    def transcribe_audio_file(self, file_path, language=None):
        """
        Transcribe an audio file using OpenAI's Whisper API.
        
        Args:
            file_path (str): Path to the audio file
            language (str, optional): Language code (e.g., 'en', 'vi')
            
        Returns:
            str: Transcribed text
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            
            # Open and transcribe the audio file
            with open(file_path, "rb") as audio_file:
                # Create transcription request
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language if language else None
                )
                
                return transcription.text
                
        except Exception as e:
            print(f"Error during transcription: {e}")
            raise
