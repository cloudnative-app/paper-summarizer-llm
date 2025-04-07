# MCP(Model Context Protocol) 시리즈

MCP(Model Context Protocol)에 대한 이해를 돕기 위한 시리즈 문서입니다. 각 편에서는 MCP의 개념, 작동 방식, 그리고 미래에 대해 자세히 알아봅니다.

## 목차

### [1편: AI 도구 연결, '표준 규격'이 필요한 이유! MCP란?](part1.md)
- MCP의 기본 개념과 필요성
- 현재 AI 도구 연결 방식의 문제점
- 표준화된 통신 방식의 중요성
- 여행 AI 도구 예시를 통한 설명

### [2편: 소통 문법(JSON-RPC)과 기본 대화 + 초간단 응답기 만들기](part2.md)
- MCP의 핵심 문법: JSON-RPC 2.0
- 기본 대화 패턴: `tools/list`, `tools/call`
- Python + Flask를 이용한 간단한 MCP 서버 구현
- 실습 가이드와 테스트 방법

### [3편: AI 시스템의 협업 방식: 서버, 클라이언트, 호스트 앱, 그리고 '만능 번역기' Transport](part3.md)
- MCP 시스템의 주요 구성 요소
- 각 구성 요소의 역할과 상호작용
- Transport 인터페이스의 개념과 중요성
- 오케스트라 비유를 통한 이해

### [4편: 표준화의 위력, 그리고 MCP가 할 수 없는 것들](part4.md)
- MCP와 Function Calling의 비교
- 표준화가 가져오는 이점
- MCP의 한계점과 주의사항
- 호스트 앱의 중요성

### [5편: MCP가 열어갈 AI 개발의 미래: 조립식 워크플로우와 공유 생태계?](part5.md)
- MCP 서버의 진화 가능성
- 워크플로우 서비스화
- 모듈 조립식 AI 개발
- MCP 서비스 마켓플레이스 전망

## 참고 자료
- [MCP 공식 웹사이트](https://modelcontextprotocol.io/)
- [MCP GitHub 저장소](https://github.com/modelcontextprotocol)

## 라이선스
이 문서는 MIT 라이선스 하에 배포됩니다.