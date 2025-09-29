#Convert text to speech using Google's
#
from gtts import gTTS
import os
# Text to convert
text= "All you can possibly need or desire is already yours. You need no helper to give it to you; it is yours now. Call your desires into being by imagining and feeling your wish fulfilled. As the end is accepted, you become totally indifferent as to possible failure, for acceptance of the end wills the means to that end. When you emerge from the moment of prayer, it is as though you were shown the happy and successful end of a play although you were not shown how that end was achieved. However, having witnessed the end, regardless of any anticlimactic sequence, you remain calm and secure in the knowledge that the end has been perfectly defined."

sourceFile="c:/Users/archangelb/Documents/texttospeech/at_your_command.txt"
destinationFile="c:/Users/archangelb/Documents/texttospeech/at_your_command.mp3"

try:
    # Open the file in read mode
    with open(sourceFile, "r") as file:
        text = file.read()

    # Create gTTS object
    tts = gTTS(text=text, tld='co.uk', lang='en')

    # Save the audio file
    print("Text loaded successfully. Now converting and saving file...")
    tts.save(destinationFile)
    print("All done.")
    print("Converted file saved to ", destinationFile)

    # Play the audio file (optional)
    #os.system(destinationFile)
    
except Exception as e:
    print("Error: ", e)
