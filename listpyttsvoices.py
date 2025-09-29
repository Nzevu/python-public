#List the voices available for use with pyttsx3
#

import pyttsx3

try:
    # Initialize the TTS engine
    engine = pyttsx3.init()
    #Get available voices
    voices = engine.getProperty('voices')

    #enumerate voices
    for voice in voices:
        print(voice.id)
        
    print("All done.")
    engine.runAndWait()
except Exception as e:
    print("Error: ", e)
    
