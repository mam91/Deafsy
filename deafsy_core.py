import speech_recognition as sr
import requests
import json
import time
import configparser
import threading
import os
import logging
import argparse

logging.basicConfig(level=logging.DEBUG)

CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deafsy_google_creds.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH

class deafsy_core(object):
    def __init__(self, config_file):
        self.listening = False
        self.config_file = config_file

        #Load settings from config and creds file
        self.load_settings()

    def load_settings(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        self.discord_endpoint = config['APPSETTINGS']['DiscordWebhookUrl']
        self.device_id = int(config['APPSETTINGS']['deviceid'])
        #with open(self.google_cloud_creds_file, 'r') as f:
        #    self.google_cloud_creds = json.load(f)

    def set_only_listening(self, value):
        self.listening = value

    def stop_listening(self):
        self.listening = False

    def listen(self):
        self.listening = True

        #Start listening thread
        thread = threading.Thread(target=self.listen_for_speech, args=())
        thread.start()

    def get_discord_endpoint(self):
        return self.discord_endpoint

    def send_chat(self, message_to_send):
        data = { "content": message_to_send }
        requests.post(self.discord_endpoint, data=data)

    def speech_to_text(self, audio):
        try:
            r = sr.Recognizer()
            speech_text = r.recognize_google_cloud(audio, language = "en-us", credentials_json = None)
            #speech_text = r.recognize_google(audio)
            logging.debug("DEBUG:Translated speech: " + speech_text)
            self.send_chat(speech_text)
        except sr.RequestError:
            # API was unreachable or unresponsive
            logging.error("ERROR:API unreachable. Exiting application.")
            self.listening = False
        except sr.UnknownValueError:
            # speech was unintelligible
            #self.send_chat("Unintelligible gibberish")
            logging.debug("DEBUG:Unintelligible gibberish")

    def listen_for_speech(self):
        #create speech recognizer
        r = sr.Recognizer()

        #try passing in device_index=0 if it doesnt work empty
        mic = sr.Microphone(device_index=self.device_id)

        #stores messages before sending to channel
        message_queue = []
        start_time = time.time()

        #listen loop should begin here
        while(self.listening):
            logging.info("Listening for voice...")
            with mic as source:
                r.adjust_for_ambient_noise(source, 0.5)
                audio = r.listen(source)

            thread = threading.Thread(target=self.speech_to_text, args=[audio])
            thread.start()


def main():
    parser = argparse.ArgumentParser(description='Translates speech to text and sends to discord channel via webhook.')
    parser.add_argument('-list_devices', help='List microphone devices', action='store_true')

    args = parser.parse_args()

    if (args.list_devices == True):
        mics = sr.Microphone.list_microphone_names()
        for i in range(len(mics)):
            logging.info("Device #: " + str(i) + " | Device name: " + mics[i])
        return

    deafsy = deafsy_core("deafsy_app.config")
    deafsy.set_only_listening(True)
    deafsy.listen_for_speech()

def kb_main():
    import keyboard  # using module keyboard
    while True:  # making a loop
        try: 
            if keyboard.key_down('q'):  # if key 'q' is pressed 
                print('You Pressed q Key!')
                break  # finishing the loop
            else:
                pass
        except:
            break


if __name__ == "__main__":
    #
    kb_main()