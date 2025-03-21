from flask import Flask, request, jsonify, Response
import core
import time
import json
import re

app = Flask(__name__)

@app.route('/v1/chat/completions', methods=['post'])
def api_send_v1_chat_completions():
    # 处理聊天请求
    data = request.get_json()
    print(data)
    if not data:
        return jsonify({'error': '未提供数据'})
    try:
        message = data['messages']
        content = message[0]['content']
        # user = data['user']
        text = core.dh.on_interact(content)
        return stream_response(text)
    except Exception as e:
        return jsonify({'error': f'处理请求时出错: {e}'}), 500

def text_chunks(text):
    pattern = r'([^.!?;:，。！？]+[.!?;:，。！？]?)'
    chunks = re.findall(pattern, text)
    for chunk in chunks:
        yield chunk

def stream_response(text):
    # 处理流式响应
    def generate():
        for chunk in text_chunks(text):
            message = {
                "id": "chatcmpl-8jqorq6Fw1Vi5XoH7pddGGpQeuPe0",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "fay-streaming",
                "choices": [
                    {
                        "delta": {
                            "content": chunk
                        },
                        "index": 0,
                        "finish_reason": None
                    }
                ]
            }
            yield f"data: {json.dumps(message)}\n\n"
            time.sleep(0.01)
        yield 'data: [DONE]\n\n'
    
    return Response(generate(), mimetype='text/event-stream')

def start():
    app.run(host='0.0.0.0', port=5000)

start()