#Convert text to speech using pyttsx3
#

import pyttsx3

try:
    # Initialize the TTS engine
    engine = pyttsx3.init()
    # Set properties (optional)
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1)  # Volume (0.0 to 1.0)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[4].id)

    #enumerate voices
    #for voice in voices:
    #    print(voice.id)
        
    #.setProperty('tld', 'co.uk')
    
    # Text to convert
    text = "Hello, this is a sample text for text-to-speech conversion."
    sourceFile="c:/Users/archangelb/Documents/texttospeech/at_your_command.txt"
    destinationFile="c:/Users/archangelb/Documents/texttospeech/at_your_command1.mp3"

    #sourceFile="c:/Users/archangelb/Documents/texttospeech/generic.txt"
    #destinationFile="c:/Users/archangelb/Documents/texttospeech/generic.mp3"

    with open(sourceFile, 'r') as file:
        text=file.read()

    # Speak the text
    #engine.say(text)

    #save to audio file
    print("Text loaded successfully. Now converting and saving file...")
    engine.save_to_file(text, destinationFile)

    print("All done.")
    engine.runAndWait()
except Exception as e:
    print("Error: ", e)
    
