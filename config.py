import os
from pathlib import Path

# 기본 경로 설정
BASE_DIR = Path(__file__).parent
INPUT_FOLDER_PATH = BASE_DIR / "input"
OUTPUT_FOLDER_PATH = BASE_DIR / "result"
PROMPT_FOLDER_PATH = BASE_DIR / "prompts"

# API 설정
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY")
MODEL_NAME = "gemini-2.0-flash"
API_CALL_DELAY = 2  # API 호출 간 지연 시간 (초)

# 로깅 설정
LOG_FILE = "gemini_responses.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = "INFO"

# CSV 파일 설정
CSV_ENCODING = 'utf-8-sig'  # Excel 호환성을 위한 인코딩

# 폴더 생성
for folder in [INPUT_FOLDER_PATH, OUTPUT_FOLDER_PATH, PROMPT_FOLDER_PATH]:
    folder.mkdir(parents=True, exist_ok=True) 