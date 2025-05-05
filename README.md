# AI-BMC (AI-powered Business Model Canvas Analyzer)

논문에서 비즈니스 모델 캔버스(BMC) 관련 내용을 자동으로 분석하는 프로그램입니다.

## 기능

- PDF 형식의 논문 파일 분석
- BMC의 9가지 구성 요소별 내용 추출
- AI 관련 특징 및 핵심 내용 분석
- 분석 결과를 CSV 파일로 저장
- 여러 논문의 분석 결과를 하나의 파일로 통합

## 파일 구조

```
.
├── analyze_paper.py    # 메인 프로그램 파일
├── input/             # 입력 PDF 파일 디렉토리
├── result/            # 분석 결과 CSV 파일 디렉토리
└── gemini_responses.log # 로그 파일
```

## 사용 방법

1. 필요한 패키지 설치:
   ```bash
   pip install google-generativeai pandas PyPDF2
   ```

2. 환경 변수 설정:
   - Google AI API 키를 환경 변수로 설정
   ```bash
   set GOOGLE_API_KEY=your_api_key
   ```

3. 입력 파일 준비:
   - `input/` 디렉토리에 분석할 PDF 파일들을 위치시킵니다.

4. 프로그램 실행:
   ```bash
   python analyze_paper.py
   ```

5. 결과 확인:
   - 개별 분석 결과: `result/논문분석_결과_[timestamp].csv`
   - 통합 분석 결과: `result/논문분석_결과_전체.csv`

## 출력 형식

분석 결과는 다음 항목들을 포함합니다:

- 논문 제목
- 핵심 내용
- AI의 특징
- BMC 9가지 구성 요소:
  - 고객 세그먼트
  - 가치 제안
  - 채널
  - 고객 관계
  - 수익 흐름
  - 핵심 자원
  - 핵심 활동
  - 핵심 파트너십
  - 비용 구조
- 추가 영역 제시
- 비즈니스 캔버스 모델의 틀 변경 제안
- 기타 특이사항 