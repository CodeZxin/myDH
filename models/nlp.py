import requests
import json
import time

prompt = "回答之前请一步一步想清楚。对于大部分问题，请直接回答并提供有用和准确的信息。所有回复请尽量控制在20字内。"

def send_request(data):
    # url = "http://dsfay.s7.tunnelfrp.com/v1/chat/completions"
    url = f"http://localhost:11434/api/chat"
    headers = {
        'Content-Type': 'application/json'
        # 'Authorization': 'Bearer sk-4Spva89SGSikpacz3a70Dd081cA84c9a8dEd345f19C9BdFc'
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        # result = response.json()
        # response_text = result["choices"][0]["message"]["content"]
        result = json.loads(response.text)
        # print(result)
        response_text = result["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        response_text = "抱歉，我现在太忙了，休息一会，请稍后再试。"
    return response_text.strip()

def question(content):
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": content}]
    data = {
        "model": "qwen2.5:0.5b",
        "messages": messages,
        # "temperature": 0.3,
        # "max_tokens": 2000,
        # "user": "user"
        "stream": False
    }
    start_time = time.time()
    response_text = send_request(data)
    print(f"NLP耗时: {time.time() - start_time:.2f} 秒")
    if "</think>" in response_text:
        response_text = response_text.split("</think>")[1]
    return response_text

if __name__ == "__main__":
    query = "你好"
    response = question(query)
    print("LLM:", response)