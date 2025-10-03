import requests
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class BackgroundGenerator:
    def __init__(self):
        self.output_dir = "backgrounds"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_scene_background(self, dialogue, scene_type="indoor"):
        """Generate AI background based on dialogue context"""
        # Simple procedural background generation
        width, height = 1920, 1080
        
        if "office" in dialogue.lower() or "work" in dialogue.lower():
            bg = self._create_office_bg(width, height)
        elif "park" in dialogue.lower() or "outside" in dialogue.lower():
            bg = self._create_outdoor_bg(width, height)
        else:
            bg = self._create_neutral_bg(width, height)
        
        filename = f"bg_{hash(dialogue) % 10000}.png"
        filepath = os.path.join(self.output_dir, filename)
        bg.save(filepath)
        return filepath
    
    def _create_office_bg(self, w, h):
        img = Image.new('RGB', (w, h), (240, 240, 245))
        draw = ImageDraw.Draw(img)
        # Simple office elements
        draw.rectangle([0, h-200, w, h], fill=(139, 69, 19))  # Floor
        draw.rectangle([w-300, 100, w-50, h-200], fill=(200, 200, 200))  # Desk
        return img
    
    def _create_outdoor_bg(self, w, h):
        img = Image.new('RGB', (w, h), (135, 206, 235))  # Sky blue
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, h-300, w, h], fill=(34, 139, 34))  # Grass
        # Simple trees
        for x in range(100, w, 400):
            draw.ellipse([x, h-400, x+100, h-300], fill=(0, 100, 0))
        return img
    
    def _create_neutral_bg(self, w, h):
        img = Image.new('RGB', (w, h), (250, 250, 250))
        draw = ImageDraw.Draw(img)
        # Gradient effect
        for y in range(h):
            color = int(250 - (y / h) * 50)
            draw.line([(0, y), (w, y)], fill=(color, color, color + 10))
        return img