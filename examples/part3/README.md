# Part 3: Transport 인터페이스 예제

이 예제는 MCP의 Transport 인터페이스를 구현한 두 가지 예제를 제공합니다:
1. HTTP를 통한 실제 통신 구현 (`HttpTransport`)
2. 테스트를 위한 Mock 구현 (`MockTransport`)

## 코드 구조

- `transport_example.py`: Transport 인터페이스와 구현체
  - `Transport`: 추상 기본 클래스
  - `HttpTransport`: HTTP 통신 구현
  - `MockTransport`: 테스트용 Mock 구현

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 실행 방법

1. 예제 실행:
```bash
python transport_example.py
```

## 코드 설명

### Transport 인터페이스
```python
class Transport(ABC):
    @abstractmethod
    def send_request(self, method: str, params: dict = None) -> dict:
        pass
```

### HttpTransport 구현
- HTTP POST 요청을 통해 MCP 메시지를 전송
- JSON-RPC 2.0 프로토콜 준수
- 실제 서버와 통신 가능

### MockTransport 구현
- 테스트를 위한 Mock 응답 제공
- 실제 서버 없이도 테스트 가능
- 미리 정의된 응답 반환

## 사용 예시

```python
# HTTP Transport 사용
http_transport = HttpTransport("http://localhost:5000")
response = http_transport.send_request("tools/list")

# Mock Transport 사용
mock_transport = MockTransport()
response = mock_transport.send_request("tools/list")
``` 