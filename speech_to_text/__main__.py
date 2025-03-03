"""
Main entry point for the Speech to Text application.
"""
import tkinter as tk
from tkinter import messagebox
import threading
import os
from PIL import Image, ImageDraw
import pyperclip

from speech_to_text.tray_icon import SystemTrayIcon
from speech_to_text.settings_manager import SettingsManager
from speech_to_text.hotkey_manager import HotkeyManager
from speech_to_text.voice_capture import VoiceRecorder
from speech_to_text.transcription_service import TranscriptionService

class SpeechToTextTrayApp:
    """The main application that runs in the system tray."""
    
    def __init__(self):
        """Initialize the application."""
        # Initialize managers and services
        self.settings_manager = SettingsManager()
        self.hotkey_manager = HotkeyManager()
        self.voice_recorder = VoiceRecorder()
        self.transcription_service = TranscriptionService()
        
        # Set up the system tray icon
        self.tray_icon = SystemTrayIcon(
            show_window_callback=self.show_settings,
            exit_callback=self.exit_app
        )
        
        # Recording state
        self.is_recording = False
        self.settings_window = None
        
        # Register the global hotkey
        activate_hotkey = self.settings_manager.get_setting('hotkeys', 'activate')
        self.hotkey_manager.register_hotkey('activate', activate_hotkey, self.toggle_recording)
        
    def run(self):
        """Run the application."""
        # Start the system tray icon
        self.tray_icon.run()
        
    def toggle_recording(self):
        """Toggle recording state when hotkey is pressed."""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
            
    def start_recording(self):
        """Start recording audio."""
        try:
            # Get the microphone device from settings
            device_id = self.settings_manager.get_setting('microphone', 'device_id')
            
            # Update UI to show recording state
            self.is_recording = True
            self.tray_icon.update_icon(recording=True)
            self.tray_icon.notify("Recording Started", "Speak now...")
            
            # Start recording
            self.voice_recorder.start_recording(device_id=device_id)
            
            # Set up a timer to automatically stop recording after max_duration
            max_duration = self.settings_manager.get_setting('recording', 'max_duration')
            threading.Timer(max_duration, self.stop_recording).start()
            
        except Exception as e:
            self.tray_icon.notify("Error", f"Failed to start recording: {str(e)}")
            self.is_recording = False
            self.tray_icon.update_icon(recording=False)
            
    def stop_recording(self):
        """Stop recording and transcribe the audio."""
        if not self.is_recording:
            return
            
        try:
            # Stop recording and get the audio file path
            audio_file = self.voice_recorder.stop_recording()
            
            if audio_file:
                # Update UI
                self.tray_icon.notify("Processing", "Transcribing your speech...")
                
                # Get selected language from settings
                language = self.settings_manager.get_setting('language')
                
                # Transcribe the audio
                text = self.transcription_service.transcribe_audio_file(audio_file, language=language)
                
                if text:
                    # Copy to clipboard or paste directly based on settings
                    if self.settings_manager.get_setting('output', 'paste_directly'):
                        # Paste the text (using pyperclip and simulating keyboard events)
                        pyperclip.copy(text)
                        
                        # Simulate Ctrl+V to paste
                        import keyboard
                        keyboard.press_and_release('ctrl+v')
                    elif self.settings_manager.get_setting('output', 'copy_to_clipboard'):
                        # Just copy to clipboard
                        pyperclip.copy(text)
                        
                    # Notify the user
                    self.tray_icon.notify("Success", "Text has been transcribed")
                else:
                    self.tray_icon.notify("Warning", "No speech detected")
                    
                # Clean up the temporary audio file
                try:
                    os.remove(audio_file)
                except:
                    pass
            else:
                self.tray_icon.notify("Warning", "No audio recorded")
                
        except Exception as e:
            self.tray_icon.notify("Error", f"Transcription failed: {str(e)}")
            
        finally:
            # Reset state
            self.is_recording = False
            self.tray_icon.update_icon(recording=False)
            
    def show_settings(self):
        """Show the settings window."""
        if self.settings_window is not None:
            # If settings window exists, just bring it to front
            self.settings_window.lift()
            self.settings_window.focus_force()
            return
            
        # Create a settings window
        self.settings_window = tk.Toplevel()
        self.settings_window.title("Speech to Text Settings")
        self.settings_window.geometry("500x400")
        self.settings_window.minsize(400, 300)
        self.settings_window.protocol("WM_DELETE_WINDOW", self.close_settings)
        
        # Add settings UI components
        self.create_settings_ui()
        
    def create_settings_ui(self):
        """Create the settings UI."""
        import tkinter.ttk as ttk
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(
            main_frame, 
            text="Speech to Text Settings",
            font=("Arial", 16, "bold")
        )
        header_label.pack(fill=tk.X, pady=(0, 20))
        
        # Create tabs
        tab_control = ttk.Notebook(main_frame)
        
        # General tab
        general_tab = ttk.Frame(tab_control)
        tab_control.add(general_tab, text="General")
        
        # Microphone selection
        mic_frame = ttk.LabelFrame(general_tab, text="Microphone Selection", padding=10)
        mic_frame.pack(fill=tk.X, pady=10)
        
        # Get available microphones
        microphones = self.voice_recorder.get_available_devices()
        mic_names = [device['name'] for device in microphones]
        
        # Current microphone
        current_mic_name = self.settings_manager.get_setting('microphone', 'device_name')
        mic_var = tk.StringVar(value=current_mic_name)
        
        # Microphone dropdown
        ttk.Label(mic_frame, text="Select Microphone:").pack(anchor=tk.W, pady=(0, 5))
        mic_dropdown = ttk.Combobox(mic_frame, textvariable=mic_var, values=mic_names, width=40)
        mic_dropdown.pack(fill=tk.X)
        
        # Language selection
        lang_frame = ttk.LabelFrame(general_tab, text="Language Selection", padding=10)
        lang_frame.pack(fill=tk.X, pady=10)
        
        # Get available languages
        languages = self.settings_manager.get_available_languages()
        lang_names = [f"{code} - {name}" for code, name in languages]
        
        # Current language
        current_lang = self.settings_manager.get_setting('language')
        lang_var = tk.StringVar(value=f"{current_lang} - {dict(languages).get(current_lang, 'Unknown')}")
        
        # Language dropdown
        ttk.Label(lang_frame, text="Select Language:").pack(anchor=tk.W, pady=(0, 5))
        lang_dropdown = ttk.Combobox(lang_frame, textvariable=lang_var, values=lang_names, width=40)
        lang_dropdown.pack(fill=tk.X)
        
        # Hotkeys tab
        hotkeys_tab = ttk.Frame(tab_control)
        tab_control.add(hotkeys_tab, text="Hotkeys")
        
        # Hotkey configuration
        hotkey_frame = ttk.LabelFrame(hotkeys_tab, text="Activation Hotkey", padding=10)
        hotkey_frame.pack(fill=tk.X, pady=10)
        
        # Current hotkey
        current_hotkey = self.hotkey_manager.get_hotkey('activate')
        hotkey_var = tk.StringVar(value=current_hotkey)
        
        # Hotkey input field
        ttk.Label(hotkey_frame, text="Press combination:").pack(anchor=tk.W, pady=(0, 5))
        hotkey_entry = ttk.Entry(hotkey_frame, textvariable=hotkey_var)
        hotkey_entry.pack(fill=tk.X, pady=5)
        
        # Record button
        record_button = ttk.Button(
            hotkey_frame,
            text="Record New Hotkey",
            command=lambda: self.record_hotkey(hotkey_var)
        )
        record_button.pack(pady=5)
        
        # Output tab
        output_tab = ttk.Frame(tab_control)
        tab_control.add(output_tab, text="Output")
        
        # Output options
        output_frame = ttk.LabelFrame(output_tab, text="Output Options", padding=10)
        output_frame.pack(fill=tk.X, pady=10)
        
        # Output checkboxes
        paste_var = tk.BooleanVar(value=self.settings_manager.get_setting('output', 'paste_directly'))
        copy_var = tk.BooleanVar(value=self.settings_manager.get_setting('output', 'copy_to_clipboard'))
        
        ttk.Checkbutton(
            output_frame,
            text="Paste text directly at cursor position",
            variable=paste_var
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Checkbutton(
            output_frame,
            text="Copy text to clipboard",
            variable=copy_var
        ).pack(anchor=tk.W, pady=5)
        
        # Recording options frame
        recording_frame = ttk.LabelFrame(output_tab, text="Recording Options", padding=10)
        recording_frame.pack(fill=tk.X, pady=10)
        
        # Max duration setting
        ttk.Label(recording_frame, text="Maximum recording duration (seconds):").pack(anchor=tk.W, pady=(0, 5))
        duration_var = tk.IntVar(value=self.settings_manager.get_setting('recording', 'max_duration'))
        duration_spinbox = ttk.Spinbox(
            recording_frame,
            from_=5,
            to=120,
            textvariable=duration_var,
            width=5
        )
        duration_spinbox.pack(anchor=tk.W)
        
        # Add tabs to window
        tab_control.pack(expand=1, fill=tk.BOTH)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Save button
        save_button = ttk.Button(
            button_frame,
            text="Save",
            command=lambda: self.save_settings(
                mic_dropdown, 
                microphones, 
                mic_var.get(),
                lang_var.get(),
                hotkey_var.get(),
                paste_var.get(),
                copy_var.get(),
                duration_var.get()
            )
        )
        save_button.pack(side=tk.RIGHT, padx=5)
        
        # Cancel button
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self.close_settings
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
    def record_hotkey(self, hotkey_var):
        """Record a new hotkey."""
        # Create a small window to capture the hotkey
        record_window = tk.Toplevel(self.settings_window)
        record_window.title("Record Hotkey")
        record_window.geometry("300x150")
        record_window.resizable(False, False)
        record_window.transient(self.settings_window)
        record_window.grab_set()
        
        # Create a label
        label = tk.Label(
            record_window,
            text="Press the keys you want to use as hotkey...",
            wraplength=250,
            pady=20
        )
        label.pack()
        
        # Variable to store the pressed keys
        keys_pressed = []
        
        def on_key(event):
            """Handle key press events."""
            key = event.keysym.lower()
            
            # Ignore duplicate keys
            if key not in keys_pressed and key not in ('shift', 'control', 'alt'):
                keys_pressed.append(key)
                
            # Construct the hotkey string
            modifiers = []
            if 'Control' in event.state:
                modifiers.append('ctrl')
            if 'Shift' in event.state:
                modifiers.append('shift')
            if 'Alt' in event.state:
                modifiers.append('alt')
                
            if keys_pressed:
                hotkey_str = '+'.join(modifiers + [keys_pressed[-1]])
                hotkey_var.set(hotkey_str)
                
                # Close the window after a short delay
                record_window.after(500, record_window.destroy)
                
        # Bind key press events
        record_window.bind('<Key>', on_key)
        
        # Button to cancel
        cancel_button = tk.Button(
            record_window,
            text="Cancel",
            command=record_window.destroy
        )
        cancel_button.pack(pady=10)
        
    def save_settings(self, mic_dropdown, microphones, mic_name, lang_str, hotkey, paste_directly, copy_to_clipboard, max_duration):
        """Save the settings."""
        try:
            # Save microphone settings
            mic_index = mic_dropdown.current()
            if mic_index >= 0:
                device_id = microphones[mic_index]['index']
                self.settings_manager.set_setting(device_id, 'microphone', 'device_id')
                self.settings_manager.set_setting(mic_name, 'microphone', 'device_name')
            
            # Save language setting
            lang_code = lang_str.split(' - ')[0]
            self.settings_manager.set_setting(lang_code, 'language')
            
            # Save hotkey setting
            current_hotkey = self.hotkey_manager.get_hotkey('activate')
            if hotkey != current_hotkey:
                # Unregister old hotkey and register new one
                self.hotkey_manager.unregister_hotkey('activate')
                self.hotkey_manager.register_hotkey('activate', hotkey, self.toggle_recording)
                self.hotkey_manager.update_hotkey('activate', hotkey)
            
            # Save output settings
            self.settings_manager.set_setting(paste_directly, 'output', 'paste_directly')
            self.settings_manager.set_setting(copy_to_clipboard, 'output', 'copy_to_clipboard')
            
            # Save recording settings
            self.settings_manager.set_setting(max_duration, 'recording', 'max_duration')
            
            # Close the settings window
            self.close_settings()
            
            # Notify the user
            self.tray_icon.notify("Settings Saved", "Your settings have been updated")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def close_settings(self):
        """Close the settings window."""
        if self.settings_window:
            self.settings_window.destroy()
            self.settings_window = None
    
    def exit_app(self):
        """Exit the application."""
        # Unregister all hotkeys
        self.hotkey_manager.unregister_all()
        
        # Stop any recording
        if self.is_recording:
            self.voice_recorder.stop_recording()
            
        # Exit the application
        import sys
        sys.exit(0)

def main():
    """Launch the Speech to Text application."""
    app = SpeechToTextTrayApp()
    app.run()
    
    # Keep the main thread running
    import time
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
