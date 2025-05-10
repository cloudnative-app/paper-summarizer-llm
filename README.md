# 논문 분석기 (Paper Analyzer)

이 프로젝트는 Gemini API를 활용하여 PDF 형식의 논문을 자동으로 분석하고 비즈니스 모델 캔버스(BMC) 관점에서 구조화된 정보를 추출하는 도구입니다.

## 주요 기능

- PDF 논문 파일 자동 분석
- Gemini API를 활용한 지능형 텍스트 분석
- 비즈니스 모델 캔버스(BMC) 관점의 구조화된 정보 추출
- CSV 형식의 분석 결과 저장
- 상세한 로깅 기능

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/cloudnative-app/paper-summarizer-llm.git
cd paper-summarizer-llm
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. Gemini API 키 설정
- Google AI Studio 또는 Cloud Console에서 API 키를 발급받습니다.
- `analyze_paper.py` 파일의 `API_KEY` 변수에 발급받은 키를 입력합니다.

## 사용 방법

1. 분석할 PDF 논문 파일을 `input` 폴더에 넣습니다.
2. 다음 명령어로 분석을 실행합니다:
```bash
python analyze_paper.py
```
3. 분석 결과는 `result` 폴더에 CSV 파일로 저장됩니다.

## 프로젝트 구조

```
paper-summarizer-llm/
├── input/              # 분석할 PDF 파일을 넣는 폴더
├── result/             # 분석 결과가 저장되는 폴더
├── analyze_paper.py    # 메인 분석 스크립트
├── requirements.txt    # 필요한 패키지 목록
└── README.md          # 프로젝트 설명 문서
```

## 분석 결과 항목

- 논문 제목
- 핵심 내용
- 비즈니스 모델 캔버스(BMC) 활용 여부
- AI의 특징
- 고객 세그먼트
- 가치 제안
- 채널
- 고객 관계
- 수익 흐름
- 핵심 자원
- 핵심 활동
- 핵심 파트너십
- 비용 구조
- 추가영역 제시
- 비즈니스 캔버스 모델의 틀 변경 여부
- 기타

## 주의사항

- API 키는 보안을 위해 환경 변수나 별도의 설정 파일로 관리하는 것을 권장합니다.
- 대량의 PDF 파일을 한 번에 처리할 경우 API 호출 제한에 주의해야 합니다.

## 라이선스

MIT License

## 기여 방법

1. 이 저장소를 포크합니다.
2. 새로운 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다. 