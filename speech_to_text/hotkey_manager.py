"""
Hotkey manager for the Speech to Text application.
Handles global hotkey registration and triggering.
"""
import keyboard
import json
import os

class HotkeyManager:
    """Manages global hotkeys for the application."""
    
    def __init__(self, config_path=None):
        """Initialize the hotkey manager."""
        self.config_path = config_path or os.path.expanduser("~/.speechtotext/config.json")
        self.hotkeys = {}
        self.default_hotkey = "ctrl+alt+v"
        self.load_config()
        
    def load_config(self):
        """Load hotkey configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    if 'hotkeys' in config:
                        self.hotkeys = config['hotkeys']
                    else:
                        self.hotkeys = {'activate': self.default_hotkey}
            else:
                # Create default configuration
                self.hotkeys = {'activate': self.default_hotkey}
                self.save_config()
        except Exception as e:
            print(f"Error loading hotkey configuration: {e}")
            self.hotkeys = {'activate': self.default_hotkey}
            
    def save_config(self):
        """Save hotkey configuration to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                json.dump({'hotkeys': self.hotkeys}, f)
                
        except Exception as e:
            print(f"Error saving hotkey configuration: {e}")
            
    def register_hotkey(self, name, key, callback):
        """Register a global hotkey."""
        if name in self.hotkeys:
            # Remove existing hotkey if it exists
            try:
                keyboard.remove_hotkey(self.hotkeys[name])
            except:
                pass
                
        # Register the new hotkey
        try:
            keyboard.add_hotkey(key, callback)
            self.hotkeys[name] = key
            self.save_config()
            return True
        except Exception as e:
            print(f"Error registering hotkey: {e}")
            return False
            
    def unregister_hotkey(self, name):
        """Unregister a global hotkey."""
        if name in self.hotkeys:
            try:
                keyboard.remove_hotkey(self.hotkeys[name])
                return True
            except Exception as e:
                print(f"Error unregistering hotkey: {e}")
                return False
        return False
        
    def get_hotkey(self, name):
        """Get the current hotkey for a specific action."""
        return self.hotkeys.get(name, self.default_hotkey)
        
    def update_hotkey(self, name, key):
        """Update a hotkey configuration."""
        self.hotkeys[name] = key
        self.save_config()
        
    def unregister_all(self):
        """Unregister all hotkeys."""
        for name, key in self.hotkeys.items():
            try:
                keyboard.remove_hotkey(key)
            except:
                pass
