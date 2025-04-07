import json
from typing import Dict, List, Any

# Function Calling 예제
class FunctionCallingExample:
    def __init__(self):
        self.functions = {
            "get_weather": {
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
        }
    
    def get_function_schema(self) -> Dict[str, Any]:
        """Function Calling 스키마 반환"""
        return {
            "functions": list(self.functions.values())
        }
    
    def handle_function_call(self, function_name: str, arguments: Dict[str, Any]) -> str:
        """Function Calling 처리"""
        if function_name == "get_weather":
            city = arguments.get("city", "")
            return f"{city}의 현재 날씨는 맑음, 기온 20°C입니다."
        return "지원하지 않는 함수입니다."

# MCP 예제
class MCPExample:
    def __init__(self):
        self.tools = [
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
    
    def handle_tools_list(self) -> Dict[str, Any]:
        """tools/list 처리"""
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": self.tools
            },
            "id": "1"
        }
    
    def handle_tools_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """tools/call 처리"""
        if name == "get_weather":
            city = arguments.get("city", "")
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": f"{city}의 현재 날씨는 맑음, 기온 20°C입니다."
                },
                "id": "1"
            }
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": f"Method {name} not found"
            },
            "id": "1"
        }

def main():
    # Function Calling 예제
    print("=== Function Calling 예제 ===")
    fc = FunctionCallingExample()
    print("Function 스키마:", json.dumps(fc.get_function_schema(), indent=2, ensure_ascii=False))
    print("Function 호출 결과:", fc.handle_function_call("get_weather", {"city": "서울"}))
    
    # MCP 예제
    print("\n=== MCP 예제 ===")
    mcp = MCPExample()
    print("tools/list 결과:", json.dumps(mcp.handle_tools_list(), indent=2, ensure_ascii=False))
    print("tools/call 결과:", json.dumps(mcp.handle_tools_call("get_weather", {"city": "서울"}), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 