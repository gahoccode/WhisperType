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
        self.pressed_keys = set()
        
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
            
    def register_hotkey(self, name, hotkey, on_press_callback, on_release_callback=None):
        """
        Register a global hotkey with press and release callbacks.
        
        Args:
            name (str): Name of the hotkey action
            hotkey (str): The hotkey combination (e.g., 'ctrl+alt+v')
            on_press_callback (callable): Function to call when all keys are pressed
            on_release_callback (callable, optional): Function to call when any key is released
        """
        if name in self.hotkeys:
            # Remove existing hotkey if it exists
            try:
                keyboard.unhook_all()
            except:
                pass
                
        # Parse the hotkey combination
        keys = hotkey.split('+')
        
        def on_key_event(e):
            if e.event_type == keyboard.KEY_DOWN:
                self.pressed_keys.add(e.name)
                # Check if all required keys are pressed
                if all(k in self.pressed_keys for k in keys):
                    on_press_callback()
            elif e.event_type == keyboard.KEY_UP:
                if e.name in self.pressed_keys:
                    self.pressed_keys.remove(e.name)
                    if on_release_callback and any(k in keys for k in [e.name]):
                        on_release_callback()
        
        # Register for all keys in the combination
        try:
            for key in keys:
                keyboard.on_press(on_key_event, suppress=True)
                keyboard.on_release(on_key_event, suppress=True)
                
            self.hotkeys[name] = hotkey
            self.save_config()
            return True
        except Exception as e:
            print(f"Error registering hotkey: {e}")
            return False
            
    def unregister_hotkey(self, name):
        """Unregister a global hotkey."""
        if name in self.hotkeys:
            try:
                keyboard.unhook_all()
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
        try:
            keyboard.unhook_all()
            self.pressed_keys.clear()
        except:
            pass
