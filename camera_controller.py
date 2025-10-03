import numpy as np
from PIL import Image
import cv2

class CameraController:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.positions = {
            'wide': (0, 0, 1.0),      # x, y, zoom
            'medium': (0, -100, 1.5),
            'close': (0, -200, 2.0),
            'left': (-200, -100, 1.5),
            'right': (200, -100, 1.5)
        }
    
    def get_camera_movement(self, scene_index, total_scenes):
        """Generate camera movement for scene"""
        movements = ['wide', 'medium', 'close', 'left', 'right']
        return movements[scene_index % len(movements)]
    
    def apply_camera_effect(self, background_img, character_frames, camera_pos):
        """Apply camera positioning and movement"""
        if not character_frames:
            return [np.array(background_img)]
        
        x_offset, y_offset, zoom = self.positions.get(camera_pos, (0, 0, 1.0))
        
        # Resize background for zoom effect
        bg = background_img.copy()
        if zoom != 1.0:
            new_w = int(self.width * zoom)
            new_h = int(self.height * zoom)
            bg = bg.resize((new_w, new_h))
            
            # Crop to original size with offset
            crop_x = max(0, (new_w - self.width) // 2 + x_offset)
            crop_y = max(0, (new_h - self.height) // 2 + y_offset)
            bg = bg.crop((crop_x, crop_y, crop_x + self.width, crop_y + self.height))
        
        # Composite character onto background
        result_frames = []
        for char_frame in character_frames:
            # Convert character frame to PIL
            char_pil = Image.fromarray(char_frame)
            
            # Create composite
            composite = bg.copy()
            
            # Position character (center-right for conversation)
            char_x = self.width - char_pil.width - 100 + x_offset
            char_y = self.height - char_pil.height - 50 + y_offset
            
            # Paste character with transparency handling
            if char_pil.mode == 'RGBA':
                composite.paste(char_pil, (char_x, char_y), char_pil)
            else:
                composite.paste(char_pil, (char_x, char_y))
            
            result_frames.append(np.array(composite))
        
        return result_frames
    
    def create_transition(self, from_pos, to_pos, frames=12):
        """Create smooth camera transition"""
        from_x, from_y, from_z = self.positions.get(from_pos, (0, 0, 1.0))
        to_x, to_y, to_z = self.positions.get(to_pos, (0, 0, 1.0))
        
        transitions = []
        for i in range(frames):
            t = i / (frames - 1)  # 0 to 1
            x = from_x + (to_x - from_x) * t
            y = from_y + (to_y - from_y) * t
            z = from_z + (to_z - from_z) * t
            transitions.append((x, y, z))
        
        return transitions