# 논문 분석 및 비즈니스 모델 캔버스 생성기

이 프로젝트는 Gemini API를 사용하여 PDF 논문을 분석하고 비즈니스 모델 캔버스(BMC)와 관련된 구조화된 정보를 추출하는 도구입니다.

## 주요 기능

- PDF 논문 텍스트 추출 및 분석
- 비즈니스 모델 캔버스 요소 자동 추출
  - 핵심 파트너십
  - 핵심 활동
  - 핵심 자원
  - 가치 제안
  - 고객 관계
  - 채널
  - 고객 세그먼트
  - 비용 구조
  - 수익원
- 사용자 정의 프롬프트 및 분석 키 지원
- CSV 형식의 구조화된 출력
- 분석 결과 시각화

## 설치 방법

1. 저장소 클론:
```bash
git clone https://github.com/yourusername/analyze-paper.git
cd analyze-paper
```

2. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

4. Gemini API 키 설정:
- Google AI Studio에서 API 키를 발급받습니다.
- `.env` 파일을 생성하고 API 키를 설정합니다:
```
GEMINI_API_KEY=your_api_key_here
```

## 사용 방법

1. 기본 사용법:
```bash
python analyze_paper.py path/to/your/paper.pdf
```

2. 사용자 정의 프롬프트 사용:
```bash
python analyze_paper.py path/to/your/paper.pdf --prompt "your_custom_prompt.txt"
```

3. 사용자 정의 분석 키 사용:
```bash
python analyze_paper.py path/to/your/paper.pdf --keys "your_custom_keys.txt"
```

## 출력 예시

```
=== 논문 분석 결과 ===
제목: [논문 제목]
저자: [저자명]
발행일: [발행일]

=== 비즈니스 모델 캔버스 요소 ===
1. 핵심 파트너십
   - [파트너십 1]
   - [파트너십 2]

2. 핵심 활동
   - [활동 1]
   - [활동 2]

[... 기타 요소들 ...]

=== 분석 결과가 'output.csv'에 저장되었습니다. ===
```

## 프로젝트 구조

```
analyze-paper/
├── analyze_paper.py      # 메인 스크립트
├── requirements.txt      # 의존성 목록
├── README.md            # 프로젝트 문서
├── prompts/             # 프롬프트 템플릿
│   └── default_prompt.txt
└── keys/                # 분석 키 정의
    └── default_keys.txt
```

## 라이선스

MIT License

## 기여 방법

1. 이슈 생성
2. 브랜치 생성
3. 변경사항 커밋
4. Pull Request 생성

## 문의사항

이슈를 통해 문의해 주세요. 