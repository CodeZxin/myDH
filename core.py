from models import nlp, tts, lip
from models.nlp import question
from models.tts import Speech
from models.lip import LipSyncGenerator
from threading import Thread
import os
from pydub import AudioSegment
import my_server

class DH():
    def __init__(self):
        self.sp = Speech()
        self.lsg = LipSyncGenerator()
        self.speaking = False

    def on_interact(self, query):
        response = question(query)
        Thread(target=self.say, args=[response]).start()
        return response
    
    def say(self, text):
        result =  self.sp.to_sample(text.replace("*", ""))
        Thread(target=self.process, args=[result, text]).start()
        return result
    
    def process(self, file_url, text):
        audio = AudioSegment.from_wav(file_url)
        audio_length = len(audio) / 1000.0  # 时长以秒为单位

        content = {
            'Topic': 'human', 
            'Data': {
                'Key': 'audio', 
                'Value': os.path.abspath(file_url),   
                'Text': text, 
                'Time': audio_length,
                "Lips": self.lsg.generate_visemes(file_url)
                }, 
            'Username' : 'User'
            }
        my_server.instance().add_cmd(content)


dh = DH() 