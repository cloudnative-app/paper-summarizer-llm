from flask import Flask, request, jsonify

app = Flask(__name__)

# 간단한 도구 목록
TOOLS = [
    {
        "name": "get_weather",
        "description": "특정 도시의 현재 날씨 정보를 가져옵니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "날씨를 확인할 도시 이름"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "translate_text",
        "description": "텍스트를 지정된 언어로 번역합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "번역할 텍스트"
                },
                "target_language": {
                    "type": "string",
                    "description": "목표 언어 (예: 'en', 'ko', 'ja')"
                }
            },
            "required": ["text", "target_language"]
        }
    }
]

@app.route('/rpc', methods=['POST'])
def handle_rpc():
    data = request.get_json()
    
    # JSON-RPC 2.0 형식 검증
    if not isinstance(data, dict) or 'jsonrpc' not in data or 'method' not in data or 'id' not in data:
        return jsonify({
            'jsonrpc': '2.0',
            'error': {
                'code': -32600,
                'message': 'Invalid Request'
            },
            'id': None
        })
    
    method = data['method']
    request_id = data['id']
    
    # tools/list 처리
    if method == 'tools/list':
        return jsonify({
            'jsonrpc': '2.0',
            'result': {
                'tools': TOOLS
            },
            'id': request_id
        })
    
    # tools/call 처리
    elif method == 'tools/call':
        if 'params' not in data:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32602,
                    'message': 'Invalid params'
                },
                'id': request_id
            })
            
        params = data['params']
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        # 도구 찾기
        tool = next((t for t in TOOLS if t['name'] == tool_name), None)
        if not tool:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32601,
                    'message': f'Method {tool_name} not found'
                },
                'id': request_id
            })
        
        # 도구 실행
        if tool_name == 'get_weather':
            city = arguments.get('city', '')
            return jsonify({
                'jsonrpc': '2.0',
                'result': {
                    'content': f"{city}의 현재 날씨는 맑음, 기온 20°C입니다."
                },
                'id': request_id
            })
        elif tool_name == 'translate_text':
            text = arguments.get('text', '')
            target_lang = arguments.get('target_language', 'en')
            return jsonify({
                'jsonrpc': '2.0',
                'result': {
                    'content': f"[{target_lang}] {text}의 번역 결과입니다."
                },
                'id': request_id
            })
    
    # 지원하지 않는 메서드
    return jsonify({
        'jsonrpc': '2.0',
        'error': {
            'code': -32601,
            'message': f'Method {method} not found'
        },
        'id': request_id
    })

if __name__ == '__main__':
    app.run(debug=True) 