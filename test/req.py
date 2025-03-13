import requests

data = {"message": "你是？", "user": "zx"}
url = "http://127.0.0.1:5000/api/chat"
# 发送 POST 请求
response = requests.post(url, json=data)
print(response.text)