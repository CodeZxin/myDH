import subprocess
import time
import os
import json

def list_files(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            print(os.path.join(root, file))

class LipSyncGenerator:
    def __init__(self):
        self.viseme_em = [
          "sil", "PP", "FF", "TH", "DD",
          "kk", "CH", "SS", "nn", "RR",
          "aa", "E", "ih", "oh", "ou"]
        self.viseme = []
        self.exe_path = os.path.join(os.getcwd(), "models", "lip_sync", "ProcessWAV.exe")

    def run_exe_and_get_output(self, arguments):
        if not os.path.exists(self.exe_path):
            raise FileNotFoundError(f"可执行文件未找到: {self.exe_path}")
        
        process = subprocess.Popen([self.exe_path] + arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                self.viseme.append(output.strip().decode())
        rc = process.poll()
        return rc

    def filter(self, viseme):
        new_viseme = []
        for v in self.viseme:
            if v in self.viseme_em:
                new_viseme.append(v)
        return new_viseme
    
    def generate_visemes(self, wav_filepath):
        wav_filepath = os.path.abspath(wav_filepath)
        arguments = ["--print-viseme-name", wav_filepath]
        start_time = time.time()
        self.run_exe_and_get_output(arguments)
        print(f"LIP耗时: {time.time() - start_time:.2f} 秒")
        visemes = self.filter(self.viseme)
        visemes = self.consolidate_visemes(visemes)
        return visemes
        
    def consolidate_visemes(self, viseme_list):
        if not viseme_list:
            return []
        result = []
        current_viseme = viseme_list[0]
        count = 1
        for viseme in viseme_list[1:]:
            if viseme == current_viseme:
                count += 1
            else:
                result.append({"Lip": current_viseme, "Time": count*33})
                current_viseme = viseme
                count = 1
        result.append({"Lip": current_viseme, "Time": count*33})
        return result
        # new_data = []
        # for i in range(len(result)):
        #     if result[i]['Time'] < 30:
        #         if len(new_data) > 0:
        #             new_data[-1]['Time'] += result[i]['Time']
        #     else:
        #         new_data.append(result[i])
        # return new_data
    
if __name__ == "__main__":
    generator = LipSyncGenerator()
    lips = generator.generate_visemes("models\\lip_sync\\test.wav")
    print(lips)
    
