# import requests

# data = {"message": "你是？", "user": "zx"}
# url = "http://127.0.0.1:5000/api/chat"
# # 发送 POST 请求
# response = requests.post(url, json=data)
# print(response.text)

import pyaudio
import wave

def record_audio(output_file, duration=5, sample_rate=16000, chunk_size=1024, channels=1):
    """
    录音并保存为 WAV 文件
    :param output_file: 输出文件名（包括路径）
    :param duration: 录音时长（秒）
    :param sample_rate: 采样率（Hz）
    :param chunk_size: 每次读取的音频数据块大小
    :param channels: 音频通道数（1 表示单声道，2 表示立体声）
    """
    # 初始化 PyAudio
    audio = pyaudio.PyAudio()

    # 打开音频流
    stream = audio.open(format=pyaudio.paInt16,  # 音频格式
                        channels=channels,       # 音频通道数
                        rate=sample_rate,        # 采样率
                        input=True,              # 输入模式
                        frames_per_buffer=chunk_size)  # 每次读取的数据块大小

    print(f"开始录音，时长 {duration} 秒...")

    # 存储音频数据
    frames = []
    for _ in range(0, int(sample_rate / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(data)

    print("录音结束！")

    # 关闭音频流
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 将音频数据保存为 WAV 文件
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

    print(f"音频已保存到 {output_file}")

# 调用函数进行录音
record_audio("output.wav", duration=10)  # 录音 10 秒，保存为 output.wav