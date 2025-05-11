# 논문 분석 도구 (Paper Analyzer)

AI 기반으로 PDF 논문을 자동 분석하여 주요 내용을 추출하고 정리해주는 프로그램입니다.

## 목차
- [주요 기능](#주요-기능)
- [설치 방법](#설치-방법)
- [사용법](#사용법)
- [폴더 구조](#폴더-구조)
- [환경설정](#환경설정)
- [분석 결과 예시](#분석-결과-예시)
- [문제 해결](#문제-해결)
- [기여 방법](#기여-방법)
- [문의](#문의)
- [Google Gemini API 키 발급 방법](#google-gemini-api-키-발급-방법-상세-안내-초보자용--현재-사용-가능-모델)

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
> **보안 주의:** API 키는 절대 analyze_paper.py 등 코드에 직접 입력하지 마세요! 반드시 config.py 또는 환경변수로만 관리하세요.

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

## Google Gemini API 키 발급 방법 상세 안내 (초보자용 + 현재 사용 가능 모델)

안녕하세요! Google의 강력한 AI 모델인 Gemini를 사용해보고 싶으신 초보자 여러분을 위해 API 키 발급 방법을 더욱 쉽고 자세하게 안내해 드립니다. 마치 옆에서 함께 컴퓨터 화면을 보며 따라 하는 것처럼 차근차근 설명해 드릴게요. 더불어 현재(2025년 5월 기준) 어떤 Gemini 모델들을 API로 사용할 수 있는지도 알려드리겠습니다.

### API 키가 무엇인가요?

API 키는 "애플리케이션 프로그래밍 인터페이스 키(Application Programming Interface Key)"의 줄임말로, 특정 프로그램이나 서비스(여기서는 Gemini)의 기능을 외부의 다른 프로그램(여러분이 만들 앱이나 서비스)에서 사용할 수 있도록 허가해 주는 일종의 비밀 열쇠입니다. 이 열쇠가 있어야 Gemini에게 "나 너의 기능을 사용해도 될까?"라고 요청하고 허락을 받을 수 있습니다.

### Gemini API 키 발급받기: 단계별 상세 가이드

#### 1단계: Google AI Studio에 접속하고 Google 계정으로 로그인하기
1. 웹 브라우저에서 [Google AI Studio](https://ai.google.dev) 또는 [aistudio.google.com](https://aistudio.google.com/)에 접속합니다.
2. Google 계정으로 로그인합니다. 계정이 없다면 새로 만드세요.

#### 2단계: API 키 발급받는 곳 찾아가기
1. 로그인 후, "Get API Key" 또는 "API 키 가져오기" 메뉴/버튼을 찾습니다.
2. 클릭하여 API 키 발급 화면으로 이동합니다.

#### 3단계: 서비스 이용 약관 동의하기
1. 약관 동의 화면이 나오면 내용을 확인하고 동의합니다.

#### 4단계: 새 프로젝트 만들고 그 안에 API 키 생성하기
1. "Create API key in new project" 버튼을 클릭합니다.
2. (선택) 프로젝트 이름을 입력합니다.

#### 5단계: API 키 확인 및 복사
1. 생성된 API 키를 복사합니다. (예: `AIzaSy***************`)
2. 안전한 곳에 저장하세요. 절대 외부에 공개하지 마세요!

#### 6단계: 결제 정보 등록하기 (필요한 경우)
1. 무료 사용량을 초과하거나 고성능 모델을 사용하려면 결제 계정을 등록해야 할 수 있습니다.
2. 신용카드 정보를 등록하고, 예산 설정도 권장합니다.

---

### 현재 (2025년 5월 기준) 사용 가능한 주요 Gemini API 모델

| 모델명 | 입력 | 출력 | 최적화 목표 |
|--------|------|------|-------------|
| **Gemini 2.5 Flash Preview 04-17**<br>gemini-2.5-flash-preview-04-17 | 오디오, 이미지, 동영상, 텍스트 | 텍스트 | 적용적 사고, 비용 효율성 |
| **Gemini 2.5 Pro 미리보기**<br>gemini-2.5-pro-preview-05-06 | 오디오, 이미지, 동영상, 텍스트 | 텍스트 | 향상된 사고 및 추론, 멀티모달 이해, 고급 코딩 등 |
| **Gemini 2.0 Flash**<br>gemini-2.0-flash | 오디오, 이미지, 동영상, 텍스트 | 텍스트 | 차세대 기능, 속도, 사고 방식, 실시간 스트리밍 |
| **Gemini 2.0 Flash 이미지 생성**<br>gemini-2.0-flash-preview-image-generation | 오디오, 이미지, 동영상, 텍스트 | 텍스트, 이미지 | 대화형 이미지 생성 및 수정 |
| **Gemini 2.0 Flash-Lite**<br>gemini-2.0-flash-lite | 오디오, 이미지, 동영상, 텍스트 | 텍스트 | 비용 효율성 및 낮은 지연 시간 |
| **Gemini 1.5 Flash**<br>gemini-1.5-flash | 오디오, 이미지, 동영상, 텍스트 | 텍스트 | 다양한 작업에서 빠르고 다재다능한 성능 |
| **Gemini 1.5 Flash-BB**<br>gemini-1.5-flash-8b | 오디오, 이미지, 동영상, 텍스트 | 텍스트 | 대용량 및 낮은 인텔리전스 태스크 |
| **Gemini 1.5 Pro**<br>gemini-1.5-pro | 오디오, 이미지, 동영상, 텍스트 | 텍스트 | 더 많은 지능이 필요한 복잡한 추론 작업 |
| **Gemini 임베딩**<br>gemini-embedding-exp | 텍스트 | 텍스트 임베딩 | 텍스트 문서와의 관련성 측정 |
| **Imagen 3**<br>imagen-3.0-generate-002 | 텍스트 | 이미지 | Google의 고급 이미지 생성 모델 |
| **Veo 2**<br>veo-2.0-generate-001 | 텍스트, 이미지 | 동영상 | 고화질 동영상 생성 |
| **Gemini 2.0 Flash 실시간**<br>gemini-2.0-flash-live-001 | 오디오, 동영상, 텍스트 | 텍스트, 오디오 | 지연 시간에 짧은 양방향 음성 및 동영상 상호작용 |

> **모델 선택 팁:** 복잡한 작업에는 최신 Pro 계열, 빠른 응답과 비용 효율이 중요하면 Flash 계열을 추천합니다.

#### 공식 문서 및 참고 링크
- [Google AI for Developers 공식 문서](https://ai.google.dev/)
- [Gemini API 모델 안내](https://ai.google.dev/models/gemini)

---

궁금한 점이 있다면 공식 문서와 커뮤니티를 적극 활용해보세요! 