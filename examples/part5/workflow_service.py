from typing import Dict, List, Any
import json
from abc import ABC, abstractmethod

class WorkflowStep(ABC):
    """워크플로우 단계 추상 클래스"""
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """단계 실행"""
        pass

class SearchStep(WorkflowStep):
    """검색 단계"""
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("query", "")
        return {
            "results": [
                {"title": f"{query} 관련 문서 1", "content": "내용 1"},
                {"title": f"{query} 관련 문서 2", "content": "내용 2"}
            ]
        }

class AnalysisStep(WorkflowStep):
    """분석 단계"""
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        results = input_data.get("results", [])
        return {
            "summary": f"검색된 {len(results)}개 문서의 분석 결과",
            "key_points": ["주요 포인트 1", "주요 포인트 2"]
        }

class WorkflowService:
    """워크플로우 서비스"""
    
    def __init__(self):
        self.steps = {
            "search": SearchStep(),
            "analyze": AnalysisStep()
        }
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """사용 가능한 도구 목록 반환"""
        return [
            {
                "name": "research_workflow",
                "description": "주제 검색 및 분석 워크플로우",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "검색할 주제"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    
    def execute_workflow(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """워크플로우 실행"""
        if name == "research_workflow":
            # 1. 검색 단계
            search_result = self.steps["search"].execute(arguments)
            
            # 2. 분석 단계
            analysis_input = {"results": search_result["results"]}
            analysis_result = self.steps["analyze"].execute(analysis_input)
            
            # 3. 결과 통합
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": {
                        "search_results": search_result,
                        "analysis": analysis_result
                    }
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
    # 워크플로우 서비스 생성
    service = WorkflowService()
    
    # 도구 목록 조회
    print("=== 도구 목록 ===")
    print(json.dumps(service.get_tools(), indent=2, ensure_ascii=False))
    
    # 워크플로우 실행
    print("\n=== 워크플로우 실행 결과 ===")
    result = service.execute_workflow(
        "research_workflow",
        {"query": "인공지능"}
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 