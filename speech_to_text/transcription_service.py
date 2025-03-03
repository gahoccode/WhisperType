"""
Transcription service for the Speech to Text application.
Handles communication with the OpenAI API for audio transcription.
"""
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

class TranscriptionService:
    """Handles audio transcription using OpenAI's Whisper API."""
    
    def __init__(self):
        """Initialize the transcription service."""
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
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
                
            # Open the audio file
            with open(file_path, "rb") as audio_file:
                # Call the OpenAI API
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
                
            # Return the transcribed text
            return response.text
            
        except Exception as e:
            print(f"Error during transcription: {e}")
            raise
            
    def transcribe_audio_file_raw(self, file_path, language=None):
        """
        Transcribe an audio file using direct API call with requests.
        This is an alternative method using direct HTTP requests.
        
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
                
            # Prepare headers and data
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": "whisper-1"
            }
            
            if language:
                data["language"] = language
                
            # Prepare the file
            files = {
                "file": open(file_path, "rb")
            }
            
            # Make the API request
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                data=data,
                files=files
            )
            
            # Close the file
            files["file"].close()
            
            # Check for errors
            if response.status_code != 200:
                raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
                
            # Parse the response
            result = response.json()
            
            # Return the transcribed text
            return result.get("text", "")
            
        except Exception as e:
            print(f"Error during transcription: {e}")
            raise
