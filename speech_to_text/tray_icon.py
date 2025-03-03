"""
System tray integration for the Speech to Text application.
"""
import pystray
from PIL import Image, ImageDraw
import tkinter as tk
import os
import sys

class SystemTrayIcon:
    """System tray icon for the Speech to Text application."""
    
    def __init__(self, show_window_callback, exit_callback):
        """Initialize the system tray icon."""
        self.show_window_callback = show_window_callback
        self.exit_callback = exit_callback
        self.icon = None
        
    def create_icon(self):
        """Create a simple icon for the system tray."""
        # Create a simple icon (a colored circle)
        icon_size = 64
        image = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Draw a blue circle with a microphone-like shape
        dc.ellipse((4, 4, icon_size-4, icon_size-4), fill=(0, 120, 212))
        dc.rectangle((24, 16, 40, 40), fill="white")
        dc.ellipse((22, 38, 42, 48), fill="white")
        
        return image
        
    def create_menu(self):
        """Create the system tray menu."""
        return pystray.Menu(
            pystray.MenuItem('Show', self.show_window),
            pystray.MenuItem('Exit', self.exit_app)
        )
        
    def show_window(self, icon, item):
        """Show the main application window."""
        if self.show_window_callback:
            self.show_window_callback()
            
    def exit_app(self, icon, item):
        """Exit the application."""
        icon.stop()
        if self.exit_callback:
            self.exit_callback()
        
    def run(self):
        """Run the system tray icon."""
        image = self.create_icon()
        menu = self.create_menu()
        
        self.icon = pystray.Icon(
            'speech-to-text',
            image,
            'Speech to Text',
            menu
        )
        
        # Run the icon in its own thread
        self.icon.run_detached()
        
    def stop(self):
        """Stop the system tray icon."""
        if self.icon:
            self.icon.stop()
            
    def update_icon(self, recording=False):
        """Update the icon to indicate recording status."""
        if self.icon:
            icon_size = 64
            image = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
            dc = ImageDraw.Draw(image)
            
            # Change color based on recording status
            if recording:
                # Red circle for recording
                dc.ellipse((4, 4, icon_size-4, icon_size-4), fill=(212, 0, 0))
            else:
                # Blue circle for standby
                dc.ellipse((4, 4, icon_size-4, icon_size-4), fill=(0, 120, 212))
                
            dc.rectangle((24, 16, 40, 40), fill="white")
            dc.ellipse((22, 38, 42, 48), fill="white")
            
            self.icon.icon = image
            
    def notify(self, title, message):
        """Show a notification from the system tray."""
        if self.icon:
            self.icon.notify(message, title)
