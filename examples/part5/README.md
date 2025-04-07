# Part 5: 워크플로우 서비스화 예제

이 예제는 MCP(Multi-Channel Protocol)를 사용하여 워크플로우를 서비스화하는 방법을 보여줍니다. 검색과 분석이라는 두 단계로 구성된 간단한 워크플로우를 구현하여, 복잡한 작업을 단계별로 처리하는 방법을 설명합니다.

## 코드 구조

- `workflow_service.py`: 워크플로우 서비스 구현
  - `WorkflowStep`: 워크플로우 단계를 정의하는 추상 클래스
  - `SearchStep`: 검색 단계 구현
  - `AnalysisStep`: 분석 단계 구현
  - `WorkflowService`: 워크플로우 서비스 메인 클래스

## 설치 방법

필요한 패키지를 설치합니다:
```bash
pip install -r requirements.txt
```

## 실행 방법

다음 명령어로 예제를 실행할 수 있습니다:
```bash
python workflow_service.py
```

## 코드 설명

### 워크플로우 단계 정의

각 워크플로우 단계는 `WorkflowStep` 추상 클래스를 상속받아 구현됩니다:

1. **SearchStep**: 주어진 쿼리로 검색을 수행하는 단계
   - 입력: 검색 쿼리
   - 출력: 검색 결과 목록

2. **AnalysisStep**: 검색 결과를 분석하는 단계
   - 입력: 검색 결과 목록
   - 출력: 분석 결과 요약 및 주요 포인트

### 워크플로우 서비스

`WorkflowService` 클래스는 MCP 형식으로 워크플로우를 서비스화합니다:

1. **도구 목록 제공**
   - `get_tools()` 메서드로 사용 가능한 워크플로우 목록 제공
   - 각 워크플로우의 입력 스키마 정의

2. **워크플로우 실행**
   - `execute_workflow()` 메서드로 워크플로우 실행
   - JSON-RPC 2.0 형식의 응답 반환
   - 오류 처리 포함

## 사용 예시

실행 결과는 다음과 같습니다:

```json
=== 도구 목록 ===
[
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

=== 워크플로우 실행 결과 ===
{
  "jsonrpc": "2.0",
  "result": {
    "content": {
      "search_results": {
        "results": [
          {"title": "인공지능 관련 문서 1", "content": "내용 1"},
          {"title": "인공지능 관련 문서 2", "content": "내용 2"}
        ]
      },
      "analysis": {
        "summary": "검색된 2개 문서의 분석 결과",
        "key_points": ["주요 포인트 1", "주요 포인트 2"]
      }
    }
  },
  "id": "1"
}
```

## 확장 가능성

이 예제는 다음과 같이 확장할 수 있습니다:

1. 새로운 워크플로우 단계 추가
2. 복잡한 워크플로우 로직 구현
3. 실제 검색 엔진 및 분석 도구 연동
4. 병렬 처리 및 에러 복구 기능 추가 