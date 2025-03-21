import os
os.environ['PATH'] += os.pathsep + os.path.join(os.getcwd(), "models")
import audioop
import math
import time
from abc import abstractmethod
from queue import Queue
from models.asr import FunASR
import numpy as np
import tempfile
import wave
from threading import Thread
from core import DH
import pyaudio

# 麦克风启动时间 (秒)
_ATTACK = 0.1

# 麦克风释放时间 (秒)
_RELEASE = 0.5


class Recorder:

    def __init__(self, dh=DH()):
        self.dh = dh
        self.__running = True
        self.__processing = False
        self.__history_level = []
        self.__history_data = []
        self.__dynamic_threshold = 0.5 # 声音识别的音量阈值
        self.__MAX_LEVEL = 25000
        self.asr = FunASR()
        self.channels = 1
        self.sample_rate = 16000
        self.stream = None
        self.id = 0

    def addjust_dynamic_threshold(self, number=30):
        total = 0
        num = 0
        for i in range(len(self.__history_level) - 1, -1, -1):
            level = self.__history_level[i]
            total += level
            num += 1
            if num >= number:
                break
            history_percentage = (total / num / self.__MAX_LEVEL) * 1.05 + 0.02
            if history_percentage > self.__dynamic_threshold:
                self.__dynamic_threshold += (history_percentage - self.__dynamic_threshold) * 0.0025
            elif history_percentage < self.__dynamic_threshold:
                self.__dynamic_threshold += (history_percentage - self.__dynamic_threshold) * 1

    def __waitingResult(self, asr, audio_data):
        self.processing = True
        t = time.time()
        tm = time.time()
        file_url = self.save_buffer_to_file(audio_data)
        self.asr.send_url(file_url)
        
        # 等待结果返回
        while not asr.done and time.time() - t < 1:
            time.sleep(0.01)
        text = asr.finalResults
        print("语音处理完成！ 耗时: {} ms".format(math.floor((time.time() - tm) * 1000)))
        if len(text) > 0:
                 self.on_speaking(text)
                 self.processing = False
        else:
            self.processing = False
            print("[!] 语音未检测到内容！")

    def __record(self):   
        try:
            stream = self.get_stream()
        except Exception as e:
            print("录音设备有误", e)
            return
        
        isSpeaking = False
        last_mute_time = time.time() #用户上次说话完话的时刻，用于VAD的开始判断（也会影响DH说完话到收听用户说话的时间间隔） 
        last_speaking_time = time.time()#用户上次说话的时刻，用于VAD的结束判断
        data = None
        audio_data_list = []
        
        while self.__running:
            try:
                data = stream.read(1024, exception_on_overflow=False)
            except Exception as e:
                data = None
                print("录音设备有误", e)
                self.__running = False
            if not data:
                continue 

            if self.dh.speaking == True:#丢弃录音
                data = None
                continue

            #计算音量是否满足激活拾音
            level = audioop.rms(data, 2)
            if len(self.__history_data) >= 10:#保存激活前的音频，以免信息掉失
                self.__history_data.pop(0)
            if len(self.__history_level) >= 500:
                self.__history_level.pop(0)
            self.__history_data.append(data)
            self.__history_level.append(level)
            percentage = level / self.__MAX_LEVEL
            
            self.addjust_dynamic_threshold()
           
            #用户正在说话，激活拾音
            try:
                if percentage > self.__dynamic_threshold:
                    last_speaking_time = time.time() 

                    if not self.__processing and not isSpeaking and time.time() - last_mute_time > _ATTACK:
                        isSpeaking = True  #用户正在说话
                        print("聆听中...")
                        self.asr.start()
                        while not self.asr.started:
                            time.sleep(0.01)
                        for i in range(len(self.__history_data) - 1): #当前data在下面会做发送，这里是发送激活前的音频数据，以免漏掉信息
                            audio_data_list.append(self.__history_data[i])
                        self.__history_data.clear()
                else:#结束拾音
                    last_mute_time = time.time()
                    if isSpeaking:
                        if time.time() - last_speaking_time > _RELEASE: 
                            isSpeaking = False
                            self.asr.end()
                            print("语音处理中...")
                            # mono_data = data = np.concatenate(audio_data_list)
                            # self.__waitingResult(self.asr, mono_data)
                            self.__save_audio_to_wav(audio_data_list, f"record/input{self.id}.wav")
                            self.id += 1
                            audio_data_list = []   
                #拾音中
                if isSpeaking:
                    audio_data_list.append(data)
            except Exception as e:
                print("录音失败: " + str(e))

    def __save_audio_to_wav(self, data, filename):
        # # 确保数据类型为 int16
        # if data.dtype != np.int16:
        #     data = data.astype(np.int16)
        
        # # 打开 WAV 文件
        with wave.open(filename, 'wb') as wf:
            # sampwidth = 2   # 16 位音频，每个采样点 2 字节
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            # wf.writeframes(data.tobytes())
            wf.writeframes(b''.join(data))

    def save_buffer_to_file(self, buffer):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir="record")
        wf = wave.open(temp_file.name, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)  
        wf.setframerate(16000)
        wf.writeframes(buffer)
        wf.close()
        return temp_file.name
    
    # #转变为单声道np.int16
    # def __process_audio_data(self, data, channels):
    #     data = bytearray(data)
    #     # 将字节数据转换为 numpy 数组
    #     data = np.frombuffer(data, dtype=np.int16)
    #     # 重塑数组，将数据分离成多个声道
    #     data = np.reshape(data, (-1, channels))
    #     # 对所有声道的数据进行平均，生成单声道
    #     mono_data = np.mean(data, axis=1).astype(np.int16)
    #     return mono_data
     
    def set_processing(self, processing):
        self.__processing = processing

    def start(self):
        Thread(target=self.__record).start()

    def stop(self):
        self.__running = False

    @abstractmethod
    def on_speaking(self, text):
        print(text)
        pass

    @abstractmethod
    def get_stream(self):
        pass

    @abstractmethod
    def is_remote(self):
        pass

class RecorderListener(Recorder):

    def __init__(self):
        super().__init__()
        # self.__device = 'device'
        # self.__FORMAT = pyaudio.paInt16
        # self.__running = False
        # self.username = 'User'
        # 这两个参数会在 get_stream 中根据实际设备更新
        # self.channels = None
        # self.sample_rate = None

    def on_speaking(self, text):
        if len(text) > 1:
            print(text)

    def get_stream(self):
        try:    
            self.paudio = pyaudio.PyAudio()
            
            # 获取默认输入设备的信息
            default_device = self.paudio.get_default_input_device_info()
            print(f"默认麦克风: {default_device.get('name')}")
            return
            self.channels = min(int(default_device.get('maxInputChannels', 1)), 2)  # 最多使用2个通道
            self.sample_rate = int(default_device.get('defaultSampleRate', 16000))
            
            print(f"默认麦克风信息 - 采样率: {self.sample_rate}Hz, 通道数: {self.channels}")
            
            # 使用系统默认麦克风
            self.stream = self.paudio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            
            self.__running = True
            Thread(target=self.__pyaudio_clear).start()
            
        except Exception as e:
            print(f"打开麦克风时出错: {str(e)}")
        return self.stream

    def __pyaudio_clear(self):
        try:
            while self.__running:
                time.sleep(30)
        except Exception as e:
            print(f"音频清理线程出错: {str(e)}")
        finally:
            if hasattr(self, 'stream') and self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except Exception as e:
                    print(f"关闭音频流时出错: {str(e)}")
    
    def stop(self):
        super().stop()
        self.__running = False
        time.sleep(0.1)#给清理线程一点处理时间
        try:
            while self.is_reading:#是为了确保停止的时候麦克风没有刚好在读取音频的
                time.sleep(0.1)
            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()
                self.paudio.terminate()
        except Exception as e:
                print(e)
                print("请检查设备是否有误，再重新启动!")

    def is_remote(self):
        return False

if __name__ == '__main__':
    recorder = RecorderListener()
    recorder.start()
    while True:
        time.sleep(1)