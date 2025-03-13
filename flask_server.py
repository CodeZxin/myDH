from flask import Flask, request, jsonify
import core
app = Flask(__name__)

@app.route('/api/chat', methods=['post'])
def api_chat():
    # 处理聊天请求
    data = request.get_json()
    if not data:
        return jsonify({'error': '未提供数据'})
    try:
        message = data['message']
        # user = data['user']
        text = core.dh.on_interact(message)
        return jsonify({'message': text})
    except Exception as e:
        return jsonify({'error': f'处理请求时出错: {e}'}), 500

# def text_chunks(text, chunk_size=20):
#     pattern = r'([^.!?;:，。！？]+[.!?;:，。！？]?)'
#     chunks = re.findall(pattern, text)
#     for chunk in chunks:
#         yield chunk

def start():
    app.run(host='0.0.0.0', port=5000)