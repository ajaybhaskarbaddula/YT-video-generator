import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
import os
from PIL import Image

class VideoComposer:
    def __init__(self):
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def compose_scene(self, background_frames, audio_path, output_path, fps=24):
        """Compose final scene with background and audio"""
        if not background_frames or not os.path.exists(audio_path):
            return None
        
        # Create video from frames
        height, width = background_frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_video = "temp_video.mp4"
        
        out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
        
        for frame in background_frames:
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)
        
        out.release()
        
        # Combine with audio using moviepy
        try:
            video_clip = VideoFileClip(temp_video)
            audio_clip = AudioFileClip(audio_path)
            
            # Match video duration to audio
            if video_clip.duration < audio_clip.duration:
                # Loop video to match audio length
                video_clip = video_clip.loop(duration=audio_clip.duration)
            else:
                # Trim video to match audio
                video_clip = video_clip.subclip(0, audio_clip.duration)
            
            final_clip = video_clip.set_audio(audio_clip)
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            # Cleanup
            video_clip.close()
            audio_clip.close()
            final_clip.close()
            
            if os.path.exists(temp_video):
                os.remove(temp_video)
            
            return output_path
            
        except Exception as e:
            print(f"Error composing video: {e}")
            if os.path.exists(temp_video):
                os.remove(temp_video)
            return None
    
    def merge_scenes(self, scene_paths, output_path):
        """Merge multiple scenes into final video"""
        if not scene_paths:
            return None
        
        try:
            clips = [VideoFileClip(path) for path in scene_paths if os.path.exists(path)]
            if not clips:
                return None
            
            final_video = CompositeVideoClip(clips, method='compose')
            final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            for clip in clips:
                clip.close()
            final_video.close()
            
            return output_path
            
        except Exception as e:
            print(f"Error merging scenes: {e}")
            return None