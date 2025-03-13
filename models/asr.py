from threading import Thread
import websocket
import json
import time
import ssl
import _thread as thread
# import my_server
import time

class FunASR:
    # 初始化
    def __init__(self, username=None):
        self.__URL = "ws://127.0.0.1:10197"
        self.__ws = None
        self.__connected = False
        self.__frames = []
        # self.__state = 0
        self.__closing = False
        # self.__task_id = ''
        self.done = False
        self.finalResults = ""
        # self.__reconnect_delay = 1
        # self.__reconnecting = False
        # self.username = username
        self.started = True

    
    # 收到websocket消息的处理
    def on_message(self, ws, message):
        try:
            self.done = True
            self.finalResults = message
            content = {
                'Topic': 'human', 
                'Data': {'Key': 'log', 'Value': self.finalResults}, 
                'Username' : 'User'
                }
            # my_server.instance().add_cmd(content)
   
        except Exception as e:
            print(e)

        if self.__closing:
            try:
                self.__ws.close()
            except Exception as e:
                print(e)

    # 收到websocket错误的处理
    def on_close(self, ws, code, msg):
        self.__connected = False
        self.__ws = None

    # 收到websocket错误的处理
    def on_error(self, ws, error):
        self.__connected = False
        self.__ws = None

    #重连
    # def __attempt_reconnect(self):
        if not self.__reconnecting:
            self.__reconnecting = True
            # util.log(1, "尝试重连funasr...")
            while not self.__connected:
                time.sleep(self.__reconnect_delay)
                self.start()
                self.__reconnect_delay *= 2  
            self.__reconnect_delay = 1  
            self.__reconnecting = False

    # 收到websocket连接建立的处理
    def on_open(self, ws):
        self.__connected = True

        def run():
            while self.__connected:
                try:
                    if len(self.__frames) > 0:
                        frame = self.__frames[0]

                        self.__frames.pop(0)
                        if type(frame) == dict:
                            ws.send(json.dumps(frame))
                        elif type(frame) == bytes:
                            ws.send(frame, websocket.ABNF.OPCODE_BINARY)
                        # print('发送 ------> ' + str(type(frame)))
                except Exception as e:
                    print(e)
                time.sleep(0.04)

        thread.start_new_thread(run, ())

    def __connect(self):
        self.finalResults = ""
        self.done = False
        self.__frames.clear()
        websocket.enableTrace(False)
        self.__ws = websocket.WebSocketApp(self.__URL, on_message=self.on_message,on_close=self.on_close,on_error=self.on_error)
        self.__ws.on_open = self.on_open
        self.__ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def send_url(self, url):
        frame = {'url' : url}
        self.__ws.send(json.dumps(frame))

    def start(self):
        Thread(target=self.__connect, args=[]).start()
        data = {
                'vad_need':False,
                'state':'StartTranscription'
        }
        self.__frames.append(data)

    def end(self):
        if self.__connected:
            try:
                for frame in self.__frames:
                    self.__frames.pop(0)
                    if type(frame) == dict:
                        self.__ws.send(json.dumps(frame))
                    elif type(frame) == bytes:
                        self.__ws.send(frame, websocket.ABNF.OPCODE_BINARY)
                self.__frames.clear()
                frame = {'vad_need':False,'state':'StopTranscription'}
                self.__ws.send(json.dumps(frame))
            except Exception as e:
                print(e)
        self.__closing = True
        self.__connected = False

if __name__ == '__main__':
    asr = FunASR()
    asr.start()
    time.sleep(3)
    asr.send_url("D:\\code\\myDH\\samples\\sample-1741594405161.wav")
    start_time = time.time()
    while not asr.done:
        time.sleep(0.01)
    print(f"ASR耗时: {time.time() - start_time:.2f} 秒")
    print("ASR结果:", asr.finalResults)