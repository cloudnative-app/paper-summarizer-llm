# 논문 분석 도구 (Paper Analyzer)

이 도구는 PDF 형식의 논문을 자동으로 분석하여 핵심 내용을 추출하고 정리해주는 프로그램입니다. Gemini AI를 활용하여 논문의 주요 내용을 분석하고, 사용자가 정의한 프롬프트 템플릿에 따라 구조화된 정보를 제공합니다.

## 주요 기능

- PDF 논문 자동 분석
- 사용자 정의 프롬프트 템플릿 기반 정보 추출
- 분석 결과를 CSV 파일로 저장
- 상세한 로그 기록

## 설치 방법

1. Python 3.8 이상이 설치되어 있어야 합니다.
2. 필요한 패키지를 설치합니다:
```bash
pip install google-generativeai
```

## 사용 방법

1. `input` 폴더에 분석하고 싶은 PDF 논문 파일을 넣습니다.
2. `prompts` 폴더에서 프롬프트 템플릿을 수정하거나 새로운 템플릿을 추가할 수 있습니다.
3. 프로그램을 실행합니다:
```bash
python analyze_paper.py
```
4. 분석 결과는 `result` 폴더에 CSV 파일로 저장됩니다.
5. 로그 파일은 `logs` 폴더에서 확인할 수 있습니다.

## 폴더 구조

```
paper-analyzer/
├── input/          # 분석할 PDF 파일을 넣는 폴더
├── result/         # 분석 결과가 저장되는 폴더
├── logs/           # 로그 파일이 저장되는 폴더
├── prompts/        # 프롬프트 템플릿 파일
├── analyze_paper.py # 메인 프로그램
└── config.py       # 설정 파일
```

## 프롬프트 템플릿

프롬프트 템플릿은 `prompts` 폴더에 JSON 형식으로 저장됩니다. 다음과 같이 템플릿을 정의하여 원하는 분석 결과를 얻을 수 있습니다:

```json
{
    "template_name": "custom_analysis",
    "fields": {
        "title": "논문 제목",
        "summary": "논문 요약",
        "key_points": "주요 포인트",
        "methodology": "연구 방법론",
        "findings": "연구 결과",
        "conclusion": "결론"
    }
}
```

## 설정 방법

1. `config.py` 파일에서 API 키를 설정합니다:
```python
API_KEY = "YOUR_API_KEY"  # Google AI Studio에서 발급받은 API 키
```

2. 필요한 경우 다음 설정을 변경할 수 있습니다:
- `MODEL_NAME`: 사용할 Gemini 모델 (기본값: "gemini-2.0-flash")
- `API_CALL_DELAY`: API 호출 간 지연 시간 (초)
- `LOG_LEVEL`: 로그 레벨 (DEBUG, INFO, WARNING, ERROR)

## 분석 결과 예시

CSV 파일에는 프롬프트 템플릿에 정의된 필드에 따라 분석된 정보가 포함됩니다. 예를 들어, 위의 템플릿을 사용할 경우 다음과 같은 정보가 포함됩니다:

- 논문 제목
- 논문 요약
- 주요 포인트
- 연구 방법론
- 연구 결과
- 결론

## 주의사항

1. Google AI Studio에서 API 키를 발급받아야 합니다.
2. 무료 API 사용량 제한이 있으므로 주의해서 사용해주세요.
3. PDF 파일은 텍스트가 추출 가능한 형식이어야 합니다.

## 문제 해결

문제가 발생하면 `logs` 폴더의 로그 파일을 확인해주세요. 주요 오류 메시지와 해결 방법:

1. API 키 오류: `config.py`의 API 키가 올바른지 확인
2. 파일 업로드 실패: PDF 파일이 손상되지 않았는지 확인
3. 분석 실패: PDF 파일의 텍스트 추출이 가능한지 확인

## 라이선스

MIT License

## 기여 방법

1. 이슈를 생성하여 버그를 보고하거나 새로운 기능을 제안해주세요.
2. Pull Request를 통해 코드 개선을 제안해주세요.

## 연락처

문제가 있거나 도움이 필요하시면 이슈를 생성해주세요. 