import pyttsx3
import os
from pathlib import Path
import streamlit as st

class VoiceGenerator:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        self.output_dir = Path("audio")
        self.output_dir.mkdir(exist_ok=True)
    
    def get_available_voices(self):
        """Get list of available voices"""
        voice_list = []
        for voice in self.voices:
            voice_list.append({
                'id': voice.id,
                'name': voice.name,
                'gender': 'Female' if 'female' in voice.name.lower() else 'Male'
            })
        return voice_list
    
    def generate_audio(self, text, voice_id, filename):
        """Generate audio file from text"""
        try:
            self.engine.setProperty('voice', voice_id)
            self.engine.setProperty('rate', 150)  # Speed
            self.engine.setProperty('volume', 0.9)  # Volume
            
            output_path = self.output_dir / f"{filename}.wav"
            self.engine.save_to_file(text, str(output_path))
            self.engine.runAndWait()
            
            return str(output_path)
        except Exception as e:
            st.error(f"Error generating audio: {e}")
            return None
    
    def generate_script_audio(self, parsed_script, voice_assignments):
        """Generate audio for entire script"""
        audio_files = []
        
        for i, item in enumerate(parsed_script):
            speaker = item['speaker']
            dialogue = item['dialogue']
            
            if speaker in voice_assignments:
                voice_id = voice_assignments[speaker]
                filename = f"{i:03d}_{speaker}"
                
                # Set voice properties once per speaker
                self.engine.setProperty('voice', voice_id)
                self.engine.setProperty('rate', 180)  # Faster speech
                self.engine.setProperty('volume', 0.9)
                
                output_path = self.output_dir / f"{filename}.wav"
                self.engine.save_to_file(dialogue, str(output_path))
                self.engine.runAndWait()
                
                if output_path.exists():
                    audio_files.append({
                        'speaker': speaker,
                        'dialogue': dialogue,
                        'audio_path': str(output_path),
                        'order': i
                    })
        
        return audio_files