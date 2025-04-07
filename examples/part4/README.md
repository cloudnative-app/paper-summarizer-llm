# Part 4: Function Calling vs MCP 비교 예제

이 예제는 Function Calling과 MCP의 차이점을 코드로 보여주는 비교 예제입니다.

## 주요 차이점

1. **프로토콜 구조**
   - Function Calling: OpenAI API에 특화된 형식
   - MCP: JSON-RPC 2.0 기반의 표준화된 프로토콜

2. **메시지 형식**
   - Function Calling: 단순한 함수 호출 형식
   - MCP: JSON-RPC 2.0의 요청-응답 구조

3. **에러 처리**
   - Function Calling: 단순한 에러 메시지
   - MCP: 표준화된 에러 코드와 메시지

## 실행 방법

```bash
python function_calling_vs_mcp.py
```

## 출력 예시

```
=== Function Calling 예제 ===
Function 스키마: {
  "functions": [
    {
      "name": "get_weather",
      "description": "특정 도시의 현재 날씨 정보를 가져옵니다.",
      "parameters": {
        "type": "object",
        "properties": {
          "city": {
            "type": "string",
            "description": "날씨를 확인할 도시 이름"
          }
        },
        "required": ["city"]
      }
    }
  ]
}
Function 호출 결과: 서울의 현재 날씨는 맑음, 기온 20°C입니다.

=== MCP 예제 ===
tools/list 결과: {
  "jsonrpc": "2.0",
  "result": {
    "tools": [
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
      }
    ]
  },
  "id": "1"
}
tools/call 결과: {
  "jsonrpc": "2.0",
  "result": {
    "content": "서울의 현재 날씨는 맑음, 기온 20°C입니다."
  },
  "id": "1"
}
```

## 코드 설명

### Function Calling 구현
- `FunctionCallingExample` 클래스
  - OpenAI API 스타일의 함수 정의
  - 단순한 함수 호출 처리

### MCP 구현
- `MCPExample` 클래스
  - JSON-RPC 2.0 프로토콜 준수
  - `tools/list`와 `tools/call` 메서드 구현
  - 표준화된 에러 처리 