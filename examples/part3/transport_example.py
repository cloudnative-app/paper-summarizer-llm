from abc import ABC, abstractmethod
import json
import requests

class Transport(ABC):
    """MCP Transport 인터페이스"""
    
    @abstractmethod
    def send_request(self, method: str, params: dict = None) -> dict:
        """MCP 요청을 전송하고 응답을 받습니다."""
        pass

class HttpTransport(Transport):
    """HTTP를 통한 MCP Transport 구현"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def send_request(self, method: str, params: dict = None) -> dict:
        """HTTP POST 요청을 통해 MCP 메시지를 전송합니다."""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": "1"  # 간단한 예제를 위해 고정 ID 사용
        }
        if params:
            payload["params"] = params
            
        response = requests.post(
            f"{self.base_url}/rpc",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        return response.json()

class MockTransport(Transport):
    """테스트를 위한 Mock Transport 구현"""
    
    def __init__(self):
        self.mock_responses = {
            "tools/list": {
                "jsonrpc": "2.0",
                "result": {
                    "tools": [
                        {
                            "name": "mock_tool",
                            "description": "테스트용 도구",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "input": {"type": "string"}
                                },
                                "required": ["input"]
                            }
                        }
                    ]
                },
                "id": "1"
            }
        }
    
    def send_request(self, method: str, params: dict = None) -> dict:
        """미리 정의된 응답을 반환합니다."""
        return self.mock_responses.get(method, {
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": f"Method {method} not found"
            },
            "id": "1"
        })

# 사용 예시
def main():
    # HTTP Transport 사용
    http_transport = HttpTransport("http://localhost:5000")
    
    # 도구 목록 조회
    tools_response = http_transport.send_request("tools/list")
    print("HTTP Transport - 도구 목록:", json.dumps(tools_response, indent=2, ensure_ascii=False))
    
    # Mock Transport 사용
    mock_transport = MockTransport()
    mock_response = mock_transport.send_request("tools/list")
    print("\nMock Transport - 도구 목록:", json.dumps(mock_response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 