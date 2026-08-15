# Core data processing
import os
import json
import numpy as np
from io import BytesIO

# Image handling
from PIL import Image  # For image processing and manipulation
from IPython.display import display

# Video and audio processing
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
# MoviePy: Essential for video creation, combining images and audio, and video editing
# Generate and display final video
import time
from IPython.display import HTML
from base64 import b64encode
# Type hints
import typing_extensions as typing

# Async support for Google API calls
import nest_asyncio
nest_asyncio.apply()
import asyncio
import contextlib
import requests
import urllib.parse
import wave  # For WAV audio file handling
from gtts import gTTS #For text to speech

# Google Generative AI
from google import genai
# Using v1alpha for the Live API for audio output. See: https://ai.google.dev/gemini-api/docs/multimodal-live
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"), http_options= {
      'api_version': 'v1alpha'
})
# Create a client for text generation using Gemini.
MODEL = "gemini-3.5-flash-lite"
# Create a client for image generation using Imagen.
IMAGE_MODEL_ID = "imagen-3.0-generate-002"
IMAGE_MODEL_ID = "imagen-4.0-generate-001"
#IMAGE_MODEL_ID = "gemini-3.1-flash-lite-image"
IMAGE_MODEL_ID = "gemini-3.1-flash-lite"


# SECTION 1: Story Generation

# Using structured output to ensure consistent story generation
# See: https://ai.google.dev/gemini-api/docs/structured-output?lang=python

# Define the structure for each story segment using TypedDict for type safety
class StorySegment(typing.TypedDict):
    image_prompt: str
    audio_text: str
    character_description: str

# Define the overall story response structure
class StoryResponse(typing.TypedDict):
    complete_story: list[StorySegment]
    pages: int

def generate_story_sequence(complete_story: str, pages: int) -> list[StorySegment]:
    response = client.models.generate_content(
        model=MODEL,
        contents=f'''you are an animation video producer. Generate a story sequence about {complete_story} in {pages} scenes (with interactions and characters), 1 sec each scene. Write:

image_prompt:(define art style for kids animation(consistent for all the characters), no violence) a full description of the scene, the characters in it, and the background in 20 words or less. Progressively shift the scene as the story advances.
audio_text: a one-sentence dialogue/narration for the scene.
character_description: no people ever, only animals and objects. Describe all characters (consistent names, features, clothing, etc.) with an art style reference (e.g., "Pixar style," "photorealistic," "Ghibli") in 30 words or less.
''',
        config={
            'response_mime_type': 'application/json',
            'response_schema': list[StoryResponse]
        }
    )

    try:
        story_data_text = response.text  # Get the JSON text
        story_data_list = json.loads(story_data_text)
        if isinstance(story_data_list, list) and len(story_data_list) > 0:
            story_data = story_data_list[0]
            return story_data.get('complete_story', []), story_data.get('character_description', {})
        else:
            return []
    except (KeyError, TypeError, IndexError, json.JSONDecodeError) as e:
        print(f"Error parsing JSON: {e}")
        return []

# SECTION 2: Image and Audio Generation
@contextlib.contextmanager
def wave_file(filename, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        yield wf

def generate_audio_live(api_text, output_filename):
    import asyncio
    collected_audio = bytearray()

    tts = gTTS(text=api_text, tld='co.uk', lang='en')
    tts.save(output_filename)
    """
    async def _generate():
        config = {
            "response_modalities": ["AUDIO"]
        }
        # Connect to the Live API using the client already initialized above.
        async with client.aio.live.connect(model=MODEL, config=config) as session:
            # Send the audio_text prompt and mark the turn complete.
            await session.send_client_content(
                turns={"role": "user", "parts": [{"text": api_text}]},
                turn_complete=True,
            )
            # Collect audio data as it streams in.
            async for response in session.receive():
                if response.data:
                    collected_audio.extend(response.data)
        return bytes(collected_audio)

    # Run the async function and collect the audio bytes.
    audio_bytes = asyncio.run(_generate())
    
    # Write the collected audio bytes into a WAV file using the helper.
    with wave_file(output_filename) as wf:
        wf.writeframes(audio_bytes)
    """
    return output_filename

# SECTION 3: Final Video Assembly and Cleanup
# Display the video in the notebook
def show_video(video_path):
    """Display video in notebook"""
    video_file = open(video_path, "rb")
    video_bytes = video_file.read()
    video_b64 = b64encode(video_bytes).decode()
    video_tag = f'<video width="640" height="480" controls><source src="data:video/mp4;base64,{video_b64}" type="video/mp4"></video>'
    return HTML(video_tag)



# SECTION 1: Story Generation
# @title Generate Story Segments
theme = "a cat and a dog playing " #@param {type:"string"}
num_scenes = 3 #@param {type:"slider", min:1, max:10, step:1}

story_segments, _ = generate_story_sequence(theme, num_scenes)
print("\nGenerated Story Segments:")
print(json.dumps(story_segments, indent=2))

# SECTION 2: Image and Audio Generation
# --- Cell 2: Definitions and setup ---
temp_audio_files = []  # To track temporary audio files
temp_image_files = []  # To track temporary image files
video_clips = []       # To store individual video clips for each scene
#image_prompts = []

# Note: Use a system instruction to prevent common AI responses and ensure natural narration
audio_negative_prompt = "don't say OK , I will do this or that, just only read this story using voice expressions without introductions or ending ,more segments are coming ,don't say OK , I will do this or that:\n"

# --- Cell 3: Main processing loop ---
for i, segment in enumerate(story_segments):
    # Retrieve details for the current scene.
    image_prompt = segment['image_prompt']
    audio_text =  audio_negative_prompt + segment['audio_text']
    audio_text_prompt = segment['audio_text']
    char_desc = segment['character_description']
    print(f"Processing scene {i}:")
    print("Image Prompt:", image_prompt)
    print("Audio Text:", audio_text_prompt)
    print("Character Description:", char_desc)
    print("--------------------------------")

    # -------------------------
    # Image Generation using Google Imagen
    # -------------------------
    combined_prompt = "detailed children book animation style " + image_prompt + " " + char_desc
    encoded_prompt = urllib.parse.quote(combined_prompt)
    IMAGE_MODEL_URL = f"https://image.pollinations.ai/prompt/{encoded_prompt}"

    print("Sending request...")
    response=requests.get(IMAGE_MODEL_URL)
    if response.status_code==200:
        #result = response.content
        image = Image.open(BytesIO(response.content))
        image_path = f"image_{i}.png"
        image.save(image_path)
        temp_image_files.append(image_path)
        #with open("couple_int.png", "wb") as f:
            #f.write(response.content)
            #print("Saved image to couple_int.png")
        image.show()
    else:
        print("Error generating image. Error code: {response.status_code}")

    
    """
    result = client.models.generate_images(
        model=IMAGE_MODEL_ID,
        prompt=combined_prompt,
        config={
            "number_of_images": 1,
            "output_mime_type": "image/jpeg",
            "person_generation": "DONT_ALLOW",
            "aspect_ratio": "1:1"
        }
    )
    

    try:
        if not result.generated_images:
            raise ValueError("No images were generated. The prompt might have been flagged as harmful. Please modify your prompt and try again.")
        for generated_image in result.generated_images:
            image = Image.open(BytesIO(generated_image.image.image_bytes))
    except Exception as e:
        print("Image generation failed ", e)

    image_path = f"image_{i}.png"
    image.save(image_path)
    temp_image_files.append(image_path)
    #display(image)
    """
    
    # -------------------------
    # Audio Generation using Google Live API
    # -------------------------
    audio_path = f"audio_{i}.wav"
    audio_path = generate_audio_live(audio_text, audio_path)
    temp_audio_files.append(audio_path)


    # -------------------------
    # Create Video Clip (Image + Audio)
    # -------------------------
    audio_clip = AudioFileClip(audio_path)

    # Convert PIL Image to numpy array
    np_image = np.array(image)

    # Create ImageClip (size is inferred from np_image)
    image_clip = ImageClip(np_image).set_duration(audio_clip.duration)

    # Store composite clip with audio in memory
    composite_clip = CompositeVideoClip([image_clip]).set_audio(audio_clip)
    video_clips.append(composite_clip)


# SECTION 3: Final Video Assembly and Cleanup

final_video = concatenate_videoclips(video_clips)
output_filename = f"{int(time.time())}_output_video.mp4"
print("Writing final video to", output_filename)
final_video.write_videofile(output_filename, fps=24)

# Show the video
#display(show_video(output_filename))
show_video(output_filename)

# Cleanup: Close video clips and remove temporary files
final_video.close()
for clip in video_clips:
    clip.close()
for file in temp_audio_files:
    os.remove(file)
for file in temp_image_files:
    os.remove(file)


# A video player will appear below
