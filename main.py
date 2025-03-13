import my_server
import flask_server
import time
import os

#音频清理
def __clear_samples():
    if not os.path.exists("./samples"):
        os.mkdir("./samples")
    for file_name in os.listdir('./samples'):
        if file_name.startswith('sample-'):
            os.remove('./samples/' + file_name)

if __name__ == '__main__':
    __clear_samples()

    dh_server = my_server.instance()
    dh_server.start_server()

    #启动http服务器
    flask_server.start()
 
    while True:
        time.sleep(1)