import streamlit as st
import os
import re
from pathlib import Path
import json
from voice_generator import VoiceGenerator
from enhanced_voice import EnhancedVoiceGenerator
from background_generator import BackgroundGenerator
from character_animator import CharacterAnimator
from camera_controller import CameraController
from video_composer import VideoComposer

# Page config
st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if 'characters' not in st.session_state:
    st.session_state.characters = {}
if 'script' not in st.session_state:
    st.session_state.script = ""
if 'parsed_script' not in st.session_state:
    st.session_state.parsed_script = []
if 'voice_generator' not in st.session_state:
    st.session_state.voice_generator = VoiceGenerator()
if 'enhanced_voice' not in st.session_state:
    st.session_state.enhanced_voice = EnhancedVoiceGenerator()
if 'bg_generator' not in st.session_state:
    st.session_state.bg_generator = BackgroundGenerator()
if 'animator' not in st.session_state:
    st.session_state.animator = CharacterAnimator()
if 'camera' not in st.session_state:
    st.session_state.camera = CameraController()
if 'composer' not in st.session_state:
    st.session_state.composer = VideoComposer()
if 'voice_assignments' not in st.session_state:
    st.session_state.voice_assignments = {}
if 'audio_files' not in st.session_state:
    st.session_state.audio_files = []
if 'generated_scenes' not in st.session_state:
    st.session_state.generated_scenes = []

def load_characters():
    """Load character images from characters folder"""
    characters_dir = Path("characters")
    characters_dir.mkdir(exist_ok=True)
    
    characters = {}
    for img_file in characters_dir.glob("*"):
        if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
            char_name = img_file.stem.lower()
            characters[char_name] = str(img_file)
    
    return characters

def parse_script(script_text):
    """Parse script to identify speakers and dialogue"""
    lines = script_text.strip().split('\n')
    parsed = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Pattern 1: "Hi, I'm John" - extract speaker from dialogue
        if "I'm" in line or "I am" in line:
            name_match = re.search(r"I[''`]?m\s+([A-Z][a-z]+)", line)
            if name_match:
                speaker = name_match.group(1).lower()
                parsed.append({
                    'speaker': speaker,
                    'dialogue': line,
                    'original_line': line
                })
                continue
        
        # Pattern 2: "Sarah replied:" or "John said:"
        speaker_match = re.search(r'([A-Z][a-z]+)\s+(replied|said):', line)
        if speaker_match:
            speaker = speaker_match.group(1).lower()
            dialogue = re.sub(r'^[^:]+:\s*', '', line).strip()
            parsed.append({
                'speaker': speaker,
                'dialogue': dialogue,
                'original_line': line
            })
            continue
        
        # Pattern 3: "Sarah: dialogue"
        colon_match = re.search(r'^([A-Z][a-z]+):\s*(.+)', line)
        if colon_match:
            speaker = colon_match.group(1).lower()
            dialogue = colon_match.group(2).strip()
            parsed.append({
                'speaker': speaker,
                'dialogue': dialogue,
                'original_line': line
            })
            continue
        
        # Default: treat as narrator
        parsed.append({
            'speaker': 'narrator',
            'dialogue': line,
            'original_line': line
        })
    
    return parsed

def main():
    st.title("🎬 AI Video Generator")
    st.markdown("Create high-quality animated videos from scripts")
    
    # Sidebar for character management
    with st.sidebar:
        st.header("📁 Character Management")
        
        # Load existing characters
        characters = load_characters()
        st.session_state.characters = characters
        
        if characters:
            st.subheader("Current Characters:")
            for char_name, char_path in characters.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.image(char_path, caption=char_name.title(), width=100)
                with col2:
                    if st.button("🗑️", key=f"del_{char_name}"):
                        os.remove(char_path)
                        st.rerun()
        
        st.subheader("Add Characters:")
        uploaded_files = st.file_uploader(
            "Upload character images", 
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="char_upload"
        )
        
        if uploaded_files:
            st.write(f"Selected {len(uploaded_files)} files:")
            for file in uploaded_files:
                char_name = st.text_input(f"Name for {file.name}:", key=f"name_{file.name}")
        
        if st.button("Save All Characters") and uploaded_files:
            characters_dir = Path("characters")
            characters_dir.mkdir(exist_ok=True)
            saved_count = 0
            
            for file in uploaded_files:
                char_name = st.session_state.get(f"name_{file.name}", "")
                if char_name:
                    file_path = characters_dir / f"{char_name.lower()}.{file.name.split('.')[-1]}"
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    saved_count += 1
            
            if saved_count > 0:
                st.success(f"Saved {saved_count} characters!")
                st.rerun()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Script Input")
        
        script_example = """Hi, I'm John. Nice to meet you!
Sarah replied: Thanks John, good to meet you too!
John said: How are you doing today?
Sarah: I'm doing great, thanks for asking!"""
        
        script_text = st.text_area(
            "Enter your script (natural conversation):",
            value=st.session_state.script,
            height=300,
            placeholder=script_example
        )
        
        if script_text != st.session_state.script:
            st.session_state.script = script_text
            st.session_state.parsed_script = parse_script(script_text)
        
        if st.button("🔍 Parse Script", type="primary"):
            st.session_state.parsed_script = parse_script(script_text)
    
    with col2:
        st.header("🎭 Script Analysis")
        
        if st.session_state.parsed_script:
            st.subheader("Detected Dialogue:")
            
            for i, item in enumerate(st.session_state.parsed_script):
                speaker = item['speaker']
                dialogue = item['dialogue']
                
                # Check if character image exists
                char_status = "✅" if speaker in st.session_state.characters else "❌"
                
                with st.expander(f"{char_status} {speaker.title()}: {dialogue[:50]}..."):
                    st.write(f"**Speaker:** {speaker.title()}")
                    st.write(f"**Dialogue:** {dialogue}")
                    st.write(f"**Original:** {item['original_line']}")
                    
                    if speaker not in st.session_state.characters and speaker != 'narrator':
                        st.warning(f"No image found for character '{speaker}'")
        
        # Voice assignment section
        st.header("🎤 Voice Assignment")
        
        if st.session_state.parsed_script:
            voices = st.session_state.voice_generator.get_available_voices()
            speakers = list(set([item['speaker'] for item in st.session_state.parsed_script]))
            
            for speaker in speakers:
                if speaker != 'narrator':
                    voice_options = [f"{v['name']} ({v['gender']})" for v in voices]
                    selected = st.selectbox(
                        f"Voice for {speaker.title()}:",
                        voice_options,
                        key=f"voice_{speaker}"
                    )
                    if selected:
                        voice_id = voices[voice_options.index(selected)]['id']
                        st.session_state.voice_assignments[speaker] = voice_id
            
            if st.button("🎵 Generate Audio", type="primary"):
                generate_audio()
        
        # Video generation section
        st.header("🎬 Video Generation")
        
        if st.session_state.audio_files:
            if st.button("🚀 Generate Video", type="primary"):
                generate_video()
        else:
            st.info("Generate audio first")

def generate_audio():
    """Generate audio from parsed script"""
    # Fast mock audio generation for testing
    audio_files = []
    
    for i, item in enumerate(st.session_state.parsed_script):
        speaker = item['speaker']
        dialogue = item['dialogue']
        
        if speaker in st.session_state.voice_assignments:
            audio_files.append({
                'speaker': speaker,
                'dialogue': dialogue,
                'audio_path': f"mock_audio_{i}.wav",
                'order': i
            })
    
    st.session_state.audio_files = audio_files
    st.success(f"Generated {len(audio_files)} audio files!")
    
    # Display mock audio info
    for audio in audio_files:
        st.write(f"🎵 **{audio['speaker'].title()}**: {audio['dialogue']}")
        st.caption(f"Voice: {st.session_state.voice_assignments[audio['speaker']]}")

def generate_video():
    """Generate video from audio and characters"""
    with st.spinner("Generating video..."):
        progress_bar = st.progress(0)
        
        # Simulate video generation process
        import time
        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)
        
        st.success("Video generated successfully!")
        st.info("Phase 3 will implement actual video creation with character animation")

if __name__ == "__main__":
    main()