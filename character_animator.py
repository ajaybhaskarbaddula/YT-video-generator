import cv2
import numpy as np
from PIL import Image, ImageDraw
import os

class CharacterAnimator:
    def __init__(self):
        self.output_dir = "animations"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def animate_character(self, char_image_path, dialogue, duration=3.0):
        """Create character animation with lip sync"""
        if not os.path.exists(char_image_path):
            return None
        
        # Load character image
        char_img = Image.open(char_image_path)
        char_img = char_img.resize((400, 600))
        
        frames = []
        fps = 24
        total_frames = int(duration * fps)
        
        for frame_num in range(total_frames):
            # Create animated frame
            frame = char_img.copy()
            
            # Simple lip sync animation
            if len(dialogue) > 0:
                mouth_open = (frame_num % 8) < 4  # Open/close cycle
                if mouth_open:
                    frame = self._add_mouth_animation(frame)
            
            # Convert to numpy array for video
            frame_array = np.array(frame)
            frames.append(frame_array)
        
        return frames
    
    def _add_mouth_animation(self, img):
        """Add simple mouth movement"""
        draw = ImageDraw.Draw(img)
        # Simple mouth position (adjust based on character)
        mouth_x, mouth_y = img.width // 2, int(img.height * 0.7)
        draw.ellipse([mouth_x-15, mouth_y-8, mouth_x+15, mouth_y+8], 
                    fill=(50, 50, 50), outline=(0, 0, 0))
        return img
    
    def create_character_video(self, frames, output_path, fps=24):
        """Convert frames to video"""
        if not frames:
            return None
        
        height, width = frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for frame in frames:
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)
        
        out.release()
        return output_path