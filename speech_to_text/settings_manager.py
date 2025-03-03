"""
Settings manager for the Speech to Text application.
Handles user preferences such as microphone selection, language, and hotkeys.
"""
import json
import os

class SettingsManager:
    """Manages application settings."""
    
    def __init__(self, config_path=None):
        """Initialize the settings manager."""
        self.config_path = config_path or os.path.expanduser("~/.speechtotext/config.json")
        
        # Default settings
        self.default_settings = {
            'microphone': {
                'device_id': None,
                'device_name': 'Default'
            },
            'language': 'en',
            'hotkeys': {
                'activate': 'ctrl+alt+v'
            },
            'output': {
                'paste_directly': True,
                'copy_to_clipboard': True
            },
            'recording': {
                'max_duration': 30  # seconds
            }
        }
        
        self.settings = self.default_settings.copy()
        self.load_settings()
        
    def load_settings(self):
        """Load settings from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_settings = json.load(f)
                    
                    # Update settings with loaded values while preserving structure
                    # and adding any new default settings
                    self._update_dict_recursively(self.settings, loaded_settings)
            else:
                # Create default settings file
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            
    def _update_dict_recursively(self, target, source):
        """Update a dictionary recursively, maintaining structure."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict_recursively(target[key], value)
            else:
                target[key] = value
                
    def save_settings(self):
        """Save settings to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Save settings
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
                
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def get_setting(self, *keys):
        """Get a setting value using dot notation."""
        current = self.settings
        for key in keys:
            if key in current:
                current = current[key]
            else:
                # Return default if key doesn't exist
                current = self.default_settings
                for k in keys:
                    if k in current:
                        current = current[k]
                    else:
                        return None
                break
        return current
        
    def set_setting(self, value, *keys):
        """Set a setting value using dot notation."""
        # Navigate to the parent of the final key
        current = self.settings
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        # Set the value at the final key
        current[keys[-1]] = value
        
        # Save the updated settings
        self.save_settings()
        
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.settings = self.default_settings.copy()
        self.save_settings()
        
    def get_available_languages(self):
        """Return a list of available languages for transcription."""
        # This could be expanded in the future
        return [
            ('en', 'English'),
            ('vi', 'Vietnamese'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German'),
            ('ja', 'Japanese'),
            ('ko', 'Korean'),
            ('zh', 'Chinese'),
            ('ru', 'Russian'),
            ('ar', 'Arabic'),
            ('pt', 'Portuguese')
        ]
