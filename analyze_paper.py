import google.generativeai as genai
import pathlib
import csv
import os
import json # JSON 파싱을 위해 추가
from datetime import datetime
import time # 지연 시간 추가를 위해
import logging  # 로깅 모듈 추가
import re  # JSON 보정용 정규식 추가
from config import *

# --- 설정 ---
# config.py에서 import된 값만 사용 (직접 할당 제거)

# 로거 설정
logger = logging.getLogger(__name__)

if API_KEY == "YOUR_API_KEY":
    logger.error("오류: 코드 내 API_KEY 변수에 실제 Gemini API 키를 입력해주세요.")
    exit()

try:
    # Gemini API 초기화
    genai.configure(api_key=API_KEY)
    logger.info("Gemini API가 초기화되었습니다.")
except Exception as e:
    logger.error(f"오류: API 초기화 중 문제가 발생했습니다 - {e}")
    exit()

# 2. 사용할 Gemini 모델 설정
# 3. PDF 파일이 있는 폴더 경로 설정
# 4. 결과를 저장할 폴더 경로 설정
# 6. API 호출 간 지연 시간 (초) - Rate Limit 방지용
# (위 변수들은 config.py에서 import된 값만 사용)

def create_output_directory(folder_path: str):
    """지정된 경로에 폴더가 없으면 생성합니다."""
    path = pathlib.Path(folder_path)
    if not path.exists():
        logger.info(f"출력 폴더 '{folder_path}'가 존재하지 않아 새로 생성합니다.")
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"오류: 출력 폴더 '{folder_path}' 생성 중 문제가 발생했습니다 - {e}")
            exit() # 폴더 생성 실패 시 프로그램 종료
    elif not path.is_dir():
        logger.error(f"오류: '{folder_path}'는 폴더가 아니라 파일입니다. 확인 후 다시 시도해주세요.")
        exit()

def upload_pdf_to_gemini(pdf_path: str) -> genai.types.File | None:
    """PDF 파일을 Gemini API에 업로드합니다."""
    path = pathlib.Path(pdf_path)
    logger.info(f"'{path.name}' 파일을 업로드하는 중...")
    try:
        pdf_file = genai.upload_file(path=path, display_name=path.name)
        logger.info(f"-> 파일 업로드 완료: {pdf_file.display_name} (URI: {pdf_file.uri})")
        logger.debug(f"파일 메타데이터: 크기={path.stat().st_size} bytes, 생성일={datetime.fromtimestamp(path.stat().st_ctime)}")
        return pdf_file
    except Exception as e:
        logger.error(f"오류: '{path.name}' 파일 업로드 중 문제 발생 - {e}", exc_info=True)
        if "rate limit" in str(e).lower():
            logger.info("   Rate limit 오류 감지. 잠시 후 재시도합니다...")
            time.sleep(API_CALL_DELAY * 5)
        return None

def analyze_pdf_with_gemini(pdf_file: genai.types.File, prompt: str) -> str:
    """Gemini API를 사용하여 PDF를 분석합니다."""
    logger.info("Gemini API로 PDF 분석 시작...")
    try:
        # Gemini API 호출
        model = genai.GenerativeModel(MODEL_NAME)
        logger.debug(f"모델 초기화 완료: {MODEL_NAME}")
        
        response = model.generate_content([prompt, pdf_file])
        logger.info("-> PDF 분석 완료")
        logger.debug(f"응답 길이: {len(response.text)} 문자")
        return response.text
    except Exception as e:
        logger.error(f"오류: PDF 분석 중 문제 발생 - {e}", exc_info=True)
        return None

def extract_json(text: str) -> dict:
    """텍스트에서 JSON 데이터를 추출합니다."""
    logger.info("JSON 데이터 추출 시작...")
    try:
        # JSON 형식 찾기
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            logger.warning("JSON 형식을 찾을 수 없습니다.")
            return None
            
        json_str = json_match.group()
        logger.debug(f"추출된 JSON 문자열 길이: {len(json_str)} 문자")
        
        # JSON 파싱
        data = json.loads(json_str)
        logger.info("-> JSON 데이터 추출 완료")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 오류: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"JSON 추출 중 예기치 않은 오류: {e}", exc_info=True)
        return None

def save_to_csv(file_path: pathlib.Path, data: dict, fieldnames: list):
    """분석 결과를 CSV 파일에 저장합니다."""
    logger.info(f"CSV 파일 저장 시작: {file_path}")
    file_exists = file_path.exists()
    try:
        with open(file_path, 'a', newline='', encoding=CSV_ENCODING) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
                logger.info(f"CSV 파일 '{file_path}' 생성 및 헤더 작성 완료")
            row_data = {field: data.get(field, "") for field in fieldnames}
            writer.writerow(row_data)
            logger.debug(f"저장된 데이터: {row_data}")
        logger.info("-> CSV 파일 저장 완료")
        return True
    except Exception as e:
        logger.error(f"오류: CSV 파일 '{file_path}' 저장 중 문제 발생 - {e}", exc_info=True)
        return False

def load_prompt_template(prompt_file: str = "default_prompt.txt") -> str:
    """프롬프트 템플릿 파일을 로드합니다."""
    prompt_path = PROMPT_FOLDER_PATH / prompt_file
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"프롬프트 템플릿 로드 실패: {e}")
        return None

def load_analysis_keys(keys_file: str = "default_keys.json") -> list:
    """분석 키 설정 파일을 로드합니다."""
    keys_path = PROMPT_FOLDER_PATH / keys_file
    try:
        with open(keys_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('keys', [])
    except Exception as e:
        logger.error(f"분석 키 로드 실패: {e}")
        return []

def safe_format_prompt(template: str, **kwargs):
    """{keys}만 남기고 나머지 { }는 모두 이스케이프"""
    def replacer(match):
        if match.group(1).strip() == 'keys':
            return '{keys}'
        return '{{' + match.group(1) + '}}'
    pattern = re.compile(r'\{([^{}]+)\}')
    safe_template = pattern.sub(replacer, template)
    return safe_template.format(**kwargs)

def main(pdf_path: str, prompt_template: str, analysis_keys: list) -> dict:
    """메인 실행 함수: PDF 업로드, 분석, 결과 반환 (단일 파일 처리)"""
    pdf_filename = pathlib.Path(pdf_path).name
    result_data = {field: "처리 시작" for field in analysis_keys}
    result_data["논문 제목"] = pdf_filename
    result_data["오류"] = ""

    # 1. PDF 파일 업로드
    uploaded_file = upload_pdf_to_gemini(pdf_path)
    if not uploaded_file:
        result_data["오류"] = "파일 업로드 실패"
        for field in analysis_keys:
            if field not in ["논문 제목", "오류"]:
                result_data[field] = "처리 중단 (업로드 실패)"
        return result_data

    # 프롬프트에 키 목록 삽입 (중괄호 자동 이스케이프)
    prompt = safe_format_prompt(prompt_template, keys=json.dumps(analysis_keys, ensure_ascii=False))
    time.sleep(API_CALL_DELAY)

    # 2. Gemini API로 분석 요청
    analysis_response_text = analyze_pdf_with_gemini(uploaded_file, prompt)

    # 3. 결과 처리
    if analysis_response_text:
        try:
            analysis_data = extract_json(analysis_response_text)
            if not analysis_data:
                result_data["오류"] = "JSON 추출 실패"
                return result_data
            
            if isinstance(analysis_data, list):
                merged_data = {}
                for item in analysis_data:
                    if isinstance(item, dict):
                        merged_data.update(item)
                analysis_data = merged_data

            for field in analysis_keys:
                if field in analysis_data:
                    result_data[field] = str(analysis_data[field])
                elif field == "논문 제목":
                    result_data[field] = pdf_filename
                else:
                    result_data[field] = "정보 없음"

        except Exception as e:
            logger.error(f"결과 처리 중 오류 발생: {e}")
            result_data["오류"] = f"결과 처리 오류: {str(e)}"
    else:
        result_data["오류"] = "API 응답 없음"

    return result_data

# --- 프로그램 실행 ---
if __name__ == "__main__":
    start_time = datetime.now()
    logger.info(f"--- 논문 분석 프로그램 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')} ---")

    # 출력 폴더 생성 확인 및 생성
    create_output_directory(OUTPUT_FOLDER_PATH)

    # 입력 폴더 경로 객체 생성 및 확인
    input_folder = pathlib.Path(INPUT_FOLDER_PATH)
    if not input_folder.is_dir():
        logger.error(f"오류: 입력 폴더 '{INPUT_FOLDER_PATH}'를 찾을 수 없습니다.")
        exit()

    # 모든 PDF 파일 처리
    pdf_files = list(input_folder.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"경고: 입력 폴더 '{INPUT_FOLDER_PATH}'에 PDF 파일이 없습니다.")
        exit()

    logger.info(f"총 {len(pdf_files)}개의 PDF 파일을 처리합니다.")
    logger.info(f"결과는 '{CSV_FILE_PATH}' 파일에 저장됩니다.")

    # 프롬프트 템플릿과 분석 키 로드
    prompt_template = load_prompt_template()
    analysis_keys = load_analysis_keys()
    
    if not prompt_template or not analysis_keys:
        logger.error("프롬프트 템플릿 또는 분석 키 로드 실패")
        exit()

    # 모든 파일 처리
    for pdf_file in pdf_files:
        try:
            logger.info(f"\n--- 파일 처리 시작: {pdf_file.name} ---")
            result = main(str(pdf_file), prompt_template, analysis_keys)
            if save_to_csv(CSV_FILE_PATH, result, analysis_keys + ["오류"]):
                logger.info(f"-> 결과 저장 완료: {pdf_file.name}")
            else:
                logger.error(f"오류: '{pdf_file.name}' 처리 결과를 CSV에 저장하지 못했습니다.")
        except Exception as e:
            logger.error(f"오류: '{pdf_file.name}' 처리 중 예기치 못한 문제 발생 - {e}")

    end_time = datetime.now()
    logger.info(f"\n--- 작업 완료: {end_time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    logger.info(f"처리 시간: {end_time - start_time}")
    logger.info(f"결과는 '{CSV_FILE_PATH}' 파일에서 확인하세요.")