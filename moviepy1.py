#Convert audio files to mp4 video files
#
from moviepy.editor import AudioFileClip, ImageClip

# Paths to your files
input_audio_path = "how_to_visualize.mp3"  # Replace with your MP3 file path
background_image_path = "see_the_end_result.png"  # Replace with your image file path
output_video_path = "how_to_visualize3.mp4"  # Desired output MP4 file path

input_audio_path = "c:/Users/archangelb/Documents/Projects/python/tut/resources/feeling_is_the_secret.mp3"
#input_video_path = "c:/Users/archangelb/Documents/Projects/python/tut/resources/how_to_visualize.mp4"
output_video_path = "c:/Users/archangelb/Documents/Projects/python/tut/resources/feeling_is_the_secret2.mp4"
background_image_path = "c:/Users/archangelb/Documents/Projects/python/tut/resources/feeling_is_the_secret.png"

try:
    # Load audio and image
    audio_clip = AudioFileClip(input_audio_path)
    image_clip = ImageClip(background_image_path)
    
    # Set the duration of the image to match the audio
    image_clip = image_clip.set_duration(audio_clip.duration)
    
    # Add audio to the image
    video_clip = image_clip.set_audio(audio_clip)
    
    # Export the video
    video_clip.write_videofile(output_video_path, fps=24)
    
    print("Conversion complete! Video saved at:", output_video_path)

except Exception as e:
    print("Error: ", e)
