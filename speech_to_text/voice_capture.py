"""
Voice capture module for the Speech to Text application.
Handles microphone input and audio processing.
"""
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import tempfile
from threading import Thread
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class VoiceRecorder:
    """Records audio from a microphone and provides visualization."""
    
    def __init__(self, sample_rate=16000, channels=1):
        """Initialize the recorder with given parameters."""
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.audio_data = []
        self.temp_dir = tempfile.gettempdir()
        self.figure = None
        self.canvas = None
        self.line = None
        self.ax = None
    
    def get_available_devices(self):
        """Return a list of available input devices."""
        devices = sd.query_devices()
        input_devices = [device for device in devices if device['max_input_channels'] > 0]
        return input_devices
    
    def start_recording(self, device_id=None):
        """Start recording audio from the microphone."""
        self.recording = True
        self.audio_data = []
        
        def callback(indata, frames, time, status):
            """Callback function for the InputStream."""
            if status:
                print(f"Status: {status}")
            self.audio_data.append(indata.copy())
            
            # Update visualization if available
            if self.line is not None and len(self.audio_data) > 0:
                try:
                    # Calculate the audio level for visualization
                    audio_segment = self.audio_data[-1].flatten()
                    level = np.abs(audio_segment).mean() * 100
                    data = np.random.rand(100) * level
                    self.line.set_ydata(data)
                    self.canvas.draw_idle()
                except Exception as e:
                    print(f"Visualization error: {e}")
        
        # Create and start the InputStream
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=callback,
            device=device_id
        )
        self.stream.start()
        return True
    
    def stop_recording(self):
        """Stop recording and save the audio to a WAV file."""
        if not self.recording:
            return None
            
        self.recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        if not self.audio_data:
            return None
            
        # Convert the recorded data to a NumPy array
        audio_data = np.concatenate(self.audio_data, axis=0)
        
        # Generate a temporary file path
        temp_file = os.path.join(self.temp_dir, 'temp_audio.wav')
        
        # Save the audio data to a WAV file
        wav.write(temp_file, self.sample_rate, audio_data)
        
        return temp_file
    
    def create_visualization(self, parent_widget):
        """Create a visualization widget for audio levels."""
        if self.figure is None:
            # Create figure and axis
            self.figure = Figure(figsize=(4, 1.5), dpi=100)
            self.ax = self.figure.add_subplot(111)
            
            # Initialize with zeros
            data = np.zeros(100)
            self.line, = self.ax.plot(np.arange(100), data)
            
            # Set axis limits and labels
            self.ax.set_ylim(0, 1)
            self.ax.set_xlim(0, 100)
            self.ax.set_title('Audio Level')
            self.ax.set_xticks([])
            
            # Create the canvas
            self.canvas = FigureCanvasTkAgg(self.figure, master=parent_widget)
            self.canvas.draw()
            
            # Get the tkinter widget
            widget = self.canvas.get_tk_widget()
            
            return widget
        return None
