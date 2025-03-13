import azure.cognitiveservices.speech as speechsdk

import time

class Speech:
    def __init__(self):
        config = speechsdk.SpeechConfig(
            subscription = "d0dfae11d1ae4095ac89adacf1998c3f",
            region = "eastasia"
        )
        config.speech_synthesis_voice_name = "zh-CN-XiaoxiaoNeural"
        # config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm)
        self.synthesizer = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=None)

    def to_sample(self, text, style=None):
        start_time = time.time()
        result =  self.synthesizer.speak_text_async(text).get()
        print(f"TTS耗时: {time.time() - start_time:.2f} 秒")
        audio_data_stream = speechsdk.AudioDataStream(result)
        file_url = './samples/sample-' + str(int(time.time() * 1000)) + '.wav'
        audio_data_stream.save_to_wav_file(file_url)
        
        return file_url

if __name__ == '__main__':
    sp = Speech()
    text = "我叫张鑫，我今年22岁。"
    s = sp.to_sample(text)