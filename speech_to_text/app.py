import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from threading import Thread
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SpeechToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech to Text Converter")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        # Configure the grid layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # Variables
        self.file_path = None
        self.transcription_in_progress = False
        
        # Create a style for the application
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TLabel', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
        
        # Create the main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky="new")
        self.main_frame.columnconfigure(0, weight=1)
        
        # Header
        header_label = ttk.Label(
            self.main_frame, 
            text="Speech to Text Converter", 
            style='Header.TLabel'
        )
        header_label.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # File selection frame
        file_frame = ttk.Frame(self.main_frame)
        file_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # File selection label
        file_label = ttk.Label(file_frame, text="Audio File:")
        file_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # File path entry
        self.file_entry = ttk.Entry(file_frame)
        self.file_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        # Browse button
        browse_button = ttk.Button(
            file_frame, 
            text="Browse", 
            command=self.browse_file
        )
        browse_button.grid(row=0, column=2, sticky="e")
        
        # Transcribe button
        self.transcribe_button = ttk.Button(
            self.main_frame,
            text="Transcribe",
            command=self.transcribe_audio,
            state="disabled"
        )
        self.transcribe_button.grid(row=2, column=0, sticky="e", pady=(0, 20))
        
        # Result frame
        result_frame = ttk.LabelFrame(root, text="Transcription Result", padding="10")
        result_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # Transcription text area
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            height=15
        )
        self.result_text.grid(row=0, column=0, sticky="nsew")
        self.result_text.config(state="disabled")
        
        # Action buttons frame
        action_frame = ttk.Frame(result_frame)
        action_frame.grid(row=1, column=0, sticky="e", pady=(10, 0))
        
        # Copy button
        self.copy_button = ttk.Button(
            action_frame,
            text="Copy to Clipboard",
            command=self.copy_to_clipboard,
            state="disabled"
        )
        self.copy_button.grid(row=0, column=0, padx=(0, 10))
        
        # Save button
        self.save_button = ttk.Button(
            action_frame,
            text="Save as Text File",
            command=self.save_to_file,
            state="disabled"
        )
        self.save_button.grid(row=0, column=1)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=2, column=0, sticky="ew")
    
    def browse_file(self):
        """Open a file dialog to select an audio file"""
        file_types = [
            ("Audio Files", "*.mp3 *.wav *.mp4 *.m4a *.webm"),
            ("All Files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=file_types
        )
        
        if file_path:
            self.file_path = file_path
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.transcribe_button.config(state="normal")
            self.status_var.set(f"Selected: {os.path.basename(file_path)}")
    
    def transcribe_audio(self):
        """Transcribe the selected audio file"""
        if not self.file_path:
            messagebox.showerror("Error", "Please select an audio file first.")
            return
        
        if self.transcription_in_progress:
            return
        
        # Check if API key is set
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            messagebox.showerror(
                "API Key Missing", 
                "Please set your OpenAI API key in the .env file."
            )
            return
        
        # Start transcription in a separate thread
        self.transcription_in_progress = True
        self.status_var.set("Transcribing... Please wait.")
        self.transcribe_button.config(state="disabled")
        
        # Reset result area
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Transcribing... Please wait.")
        self.result_text.config(state="disabled")
        
        # Start the transcription in a background thread
        thread = Thread(target=self.perform_transcription)
        thread.daemon = True
        thread.start()
    
    def perform_transcription(self):
        """Background task for performing the transcription"""
        try:
            # Initialize OpenAI client
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Perform transcription
            with open(self.file_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            # Update the result text area
            self.root.after(0, self.update_transcription_result, transcription.text)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
        
        finally:
            self.root.after(0, self.reset_transcription_state)
    
    def update_transcription_result(self, text):
        """Update the result text area with transcription"""
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state="disabled")
        
        # Enable action buttons
        self.copy_button.config(state="normal")
        self.save_button.config(state="normal")
        
        # Update status
        self.status_var.set("Transcription completed")
    
    def show_error(self, error_message):
        """Show error message"""
        messagebox.showerror("Error", f"Transcription failed: {error_message}")
        
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Error: {error_message}")
        self.result_text.config(state="disabled")
    
    def reset_transcription_state(self):
        """Reset the transcription state"""
        self.transcription_in_progress = False
        self.transcribe_button.config(state="normal")
    
    def copy_to_clipboard(self):
        """Copy transcription to clipboard"""
        text = self.result_text.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_var.set("Copied to clipboard")
    
    def save_to_file(self):
        """Save transcription to a text file"""
        text = self.result_text.get(1.0, tk.END).strip()
        if not text:
            return
        
        # Open save dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Transcription"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(text)
                self.status_var.set(f"Saved to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
