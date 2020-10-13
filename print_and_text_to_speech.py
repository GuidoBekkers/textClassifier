from gtts import gTTS
from playsound import playsound
import time


def print_and_text_to_speech(string, tts):
    """Takes a string as input and prints it. If the user wants text-to-speech conversion, this function also converts
    and plays the speech
    Parameters
    ----------
    string : str
        the string that will be either printed and then converted to speech, or just printed
    tts : bool
        the boolean that determines whether or not text to speech is on
    Returns
    -------
    Doesn't return, only prints and if applicable plays the speech file
    """

    # global tts

    print(string)

    if tts:
        language = 'en'

        sound_to_play = gTTS(text=string, lang=language, slow=False)

        unique_name = time.time()

        sound_to_play.save("tts_mp3/{0}_text_to_speech.mp3".format(unique_name))

        playsound("tts_mp3/{0}_text_to_speech.mp3".format(unique_name))
