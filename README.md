# 논문 분석기 (Paper Analyzer)

이 프로젝트는 Gemini API를 활용하여 PDF 형식의 논문을 자동으로 분석하고 비즈니스 모델 캔버스(BMC) 관점에서 구조화된 정보를 추출하는 도구입니다.

## 주요 기능

- PDF 논문 파일 자동 분석
- Gemini API를 활용한 지능형 텍스트 분석
- 비즈니스 모델 캔버스(BMC) 관점의 구조화된 정보 추출
- CSV 형식의 분석 결과 저장
- 상세한 로깅 기능
- 사용자 정의 프롬프트 및 분석 키 지원

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
- `config.py` 파일의 `API_KEY` 변수에 발급받은 키를 입력하거나 환경 변수로 설정합니다:
  ```bash
  # Windows
  set GEMINI_API_KEY=your_api_key
  
  # Linux/Mac
  export GEMINI_API_KEY=your_api_key
  ```

## 사용 방법

1. 분석할 PDF 논문 파일을 `input` 폴더에 넣습니다.
2. 필요한 경우 프롬프트와 분석 키를 수정합니다:
   - `prompts/default_prompt.txt`: 분석 프롬프트 템플릿
   - `prompts/default_keys.json`: 분석할 키 목록
3. 다음 명령어로 분석을 실행합니다:
```bash
python analyze_paper.py
```
4. 분석 결과는 `result` 폴더에 CSV 파일로 저장됩니다.

## 프로젝트 구조

```
paper-summarizer-llm/
├── input/              # 분석할 PDF 파일을 넣는 폴더
├── result/             # 분석 결과가 저장되는 폴더
├── prompts/            # 프롬프트 및 분석 키 설정 폴더
│   ├── default_prompt.txt  # 기본 프롬프트 템플릿
│   └── default_keys.json   # 기본 분석 키 설정
├── analyze_paper.py    # 메인 분석 스크립트
├── config.py           # 설정 파일
├── requirements.txt    # 필요한 패키지 목록
└── README.md          # 프로젝트 설명 문서
```

## 프롬프트 및 분석 키 커스터마이징

### 프롬프트 템플릿 수정
`prompts/default_prompt.txt` 파일을 수정하여 분석 프롬프트를 커스터마이징할 수 있습니다. 프롬프트 템플릿에는 `{keys}` 플레이스홀더가 포함되어 있어야 하며, 이는 분석 키 목록으로 대체됩니다.

### 분석 키 수정
`prompts/default_keys.json` 파일을 수정하여 분석할 키를 추가하거나 제거할 수 있습니다. 파일 형식은 다음과 같습니다:
```json
{
    "keys": [
        "키1",
        "키2",
        "키3"
    ]
}
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
- 프롬프트 템플릿을 수정할 때는 `{keys}` 플레이스홀더를 반드시 포함해야 합니다.

## 라이선스

MIT License

## 기여 방법

1. 이 저장소를 포크합니다.
2. 새로운 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다. 