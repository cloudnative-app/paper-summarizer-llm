import os
from pathlib import Path
from datetime import datetime

# 기본 경로 설정
BASE_DIR = Path(__file__).parent
INPUT_FOLDER_PATH = BASE_DIR / "input"
OUTPUT_FOLDER_PATH = BASE_DIR / "result"
PROMPT_FOLDER_PATH = BASE_DIR / "prompts"
LOG_FOLDER_PATH = BASE_DIR / "logs"

# API 설정
API_KEY = "AIzaSyB1te7hQnMp6v5nyQgv_F2uUMjTonbSjDs"  # API 키 직접 설정
MODEL_NAME = "gemini-2.0-flash"  # Gemini 2.0 버전 사용
API_CALL_DELAY = 2  # API 호출 간 지연 시간 (초)

# 로깅 설정
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOG_FOLDER_PATH / f"analyze_paper_{current_time}.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
LOG_LEVEL = "DEBUG"  # 더 자세한 로깅을 위해 DEBUG 레벨로 변경

# 로그 파일 설정
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5  # 최대 5개의 백업 파일 유지

# CSV 파일 설정
CSV_ENCODING = 'utf-8-sig'  # Excel 호환성을 위한 인코딩

# 폴더 생성
for folder in [INPUT_FOLDER_PATH, OUTPUT_FOLDER_PATH, PROMPT_FOLDER_PATH, LOG_FOLDER_PATH]:
    folder.mkdir(parents=True, exist_ok=True) 