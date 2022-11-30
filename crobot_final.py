from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
import speech_recognition as sr
import re
from googletrans import Translator
import azure.cognitiveservices.speech as speechsdk
import wikipedia
import datetime


# Creates an instance of a speech config with specified subscription key and service region.
# Replace with your own subscription key and service region (e.g., "westus").
speech_key, service_region = "*************", "westeurope"
speech_config = speechsdk.SpeechConfig(
    subscription=speech_key, region=service_region)

# Sets the synthesis language.
# The full list of supported languages can be found here:
# https://docs.microsoft.com/azure/cognitive-services/speech-service/language-support#text-to-speech
language = "hr-HR"
speech_config.speech_synthesis_language = language

# Creates a speech synthesizer using the default speaker as audio output.
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

mname = 'facebook/blenderbot-400M-distill'
model = BlenderbotForConditionalGeneration.from_pretrained(mname)
tokenizer = BlenderbotTokenizer.from_pretrained(mname)


def azure_speak(question):
    speech_synthesizer.speak_text_async(question).get()


def welcome_message():

    hour = datetime.datetime.now().hour

    if hour >= 6 and hour <= 12:
        azure_speak("Dobro jutro")
    elif hour > 12 and hour < 18:
        azure_speak("Dobar dan")
    elif hour > 18 and hour <= 24:
        azure_speak("Dobra večer")

    azure_speak("Moje ime je KroBot. Kako ti mogu pomoći?")


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="hr-HR")
        if "kraj" in query:
            return query
        else:
            translator = Translator()
            en_query = translator.translate(query, dest='en').text
            print("Print out: ", en_query)
    except Exception as e:
        print(e)
        azure_speak("Molim te, ponovi mi pitanje...")

        return takeCommand()

    return en_query


if __name__ == "__main__":

    welcome_message()

    
    while True:
        translator = Translator()
        query = takeCommand().lower()
        print(query)
        if "wikipedi" in query:
            azure_speak("Molim te izgovori pojam koji želiš da pretražim na Vikipediji...")
            translator = Translator()
            wiki_query = takeCommand().lower()
            try:
                azure_speak("Pretražujem...")
                print(wiki_query)
                result = wikipedia.summary(wiki_query, sentences=2)
                hr_result = translator.translate(result, dest='hr').text
                azure_speak(hr_result)
            except Exception as e:
                print(e)
                azure_speak("Dogodila se greška u pretraživanju...")
        elif "wikipedi" not in query and "kraj" not in query:
            UTTERANCE = query
            print(f">> User: {UTTERANCE}")
            inputs = tokenizer([UTTERANCE], return_tensors='pt')
            reply_ids = model.generate(**inputs)
            print(">> Blenderbot: ")
            replica = tokenizer.batch_decode(reply_ids)
            replica[0] = re.sub('(<s>)|(</s>)', '', replica[0])
            str_replica = ' '.join(replica)
            hr_replica = translator.translate(str_replica, dest='hr').text
            print(hr_replica)
            azure_speak(hr_replica)
        elif "kraj" in query:
            azure_speak("Završavam razgovor... Želim ti ugodan ostatak dana!")
            break
