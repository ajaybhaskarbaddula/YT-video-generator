import pyttsx3
import os
from pathlib import Path
import json

class EnhancedVoiceGenerator:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        self.output_dir = Path("audio")
        self.output_dir.mkdir(exist_ok=True)
        self.character_voices = self._load_voice_profiles()
    
    def _load_voice_profiles(self):
        """Load character-specific voice profiles"""
        return {
            'john': {'rate': 160, 'volume': 0.9, 'pitch': 0},
            'sarah': {'rate': 150, 'volume': 0.8, 'pitch': 50},
            'mike': {'rate': 140, 'volume': 1.0, 'pitch': -20},
            'emma': {'rate': 155, 'volume': 0.85, 'pitch': 30}
        }
    
    def get_character_voice(self, character_name):
        """Get optimized voice settings for character"""
        char_lower = character_name.lower()
        
        # Select voice based on character
        if char_lower in self.character_voices:
            profile = self.character_voices[char_lower]
        else:
            # Default profile
            profile = {'rate': 150, 'volume': 0.9, 'pitch': 0}
        
        # Select appropriate system voice
        female_voices = [v for v in self.voices if 'female' in v.name.lower()]
        male_voices = [v for v in self.voices if 'male' in v.name.lower() or 'david' in v.name.lower()]
        
        if char_lower in ['sarah', 'emma'] and female_voices:
            voice_id = female_voices[0].id
        elif male_voices:
            voice_id = male_voices[0].id
        else:
            voice_id = self.voices[0].id if self.voices else None
        
        return voice_id, profile
    
    def generate_enhanced_audio(self, text, character_name, filename):
        """Generate audio with character-specific voice settings"""
        voice_id, profile = self.get_character_voice(character_name)
        
        if not voice_id:
            return None
        
        try:
            self.engine.setProperty('voice', voice_id)
            self.engine.setProperty('rate', profile['rate'])
            self.engine.setProperty('volume', profile['volume'])
            
            output_path = self.output_dir / f"{filename}.wav"
            self.engine.save_to_file(text, str(output_path))
            self.engine.runAndWait()
            
            return str(output_path)
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None
    
    def get_audio_duration(self, text, character_name):
        """Estimate audio duration for timing"""
        _, profile = self.get_character_voice(character_name)
        words_per_minute = profile['rate'] * 0.8  # Approximate
        word_count = len(text.split())
        duration = (word_count / words_per_minute) * 60
        return max(duration, 1.0)  # Minimum 1 second