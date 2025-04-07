# Part 2: 간단한 MCP 서버 예제

이 예제는 MCP(Model Context Protocol)의 기본적인 구현을 보여주는 간단한 서버입니다.

## 기능

- `tools/list`: 사용 가능한 도구 목록 제공
- `tools/call`: 도구 실행 요청 처리
  - `get_weather`: 도시의 날씨 정보 제공
  - `translate_text`: 텍스트 번역

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 실행 방법

1. 서버 실행:
```bash
python simple_mcp_server.py
```

2. API 테스트:
```bash
# 도구 목록 조회
curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "id": "1", "method": "tools/list"}' http://127.0.0.1:5000/rpc

# 날씨 정보 조회
curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "id": "2", "method": "tools/call", "params": {"name": "get_weather", "arguments": {"city": "서울"}}}' http://127.0.0.1:5000/rpc

# 텍스트 번역
curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "id": "3", "method": "tools/call", "params": {"name": "translate_text", "arguments": {"text": "안녕하세요", "target_language": "en"}}}' http://127.0.0.1:5000/rpc
```

## 코드 설명

- `simple_mcp_server.py`: MCP 서버 구현
  - Flask를 사용한 HTTP 서버
  - JSON-RPC 2.0 프로토콜 구현
  - 도구 목록 및 실행 기능 제공 