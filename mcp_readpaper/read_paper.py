import os
import fitz  # PyMuPDF
import pandas as pd
import json
import logging
import argparse
import re
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import time
from datetime import datetime
from PyPDF2 import PdfReader
from prompt_loader import (
    load_questions_from_md,
    load_prompt_template,
    create_analysis_prompt,
    create_error_response,
    create_default_response,
    create_structured_answer,
    validate_json_response
)
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor

# 결과 디렉토리 설정
RESULTS_DIR = {
    "raw": os.path.join("results", "raw"),
    "processed": os.path.join("results", "processed"),
    "logs": os.path.join("results", "logs")
}

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(RESULTS_DIR["logs"], 'paper_analysis.log'), encoding='utf-8', mode='a'),
        logging.StreamHandler()
    ]
)

# 환경 변수 로드
load_dotenv()

# 기본 설정값 정의
DEFAULT_CONFIG = {
    "PDF_DIR": "./pdfs",
    "CHUNK_SIZE": "15000",
    "MAX_RETRIES": "3",
    "GOOGLE_API_KEY": None  # API 키는 반드시 .env 파일에서 설정해야 함
}

# 환경 변수가 없는 경우 기본값 사용
for key, value in DEFAULT_CONFIG.items():
    if not os.getenv(key):
        os.environ[key] = value

# PDF 디렉토리 경로 설정
PDF_DIR = os.getenv("PDF_DIR")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES"))

# CSV 컬럼 매핑 정의
COLUMN_MAP = {
    "논문 제목": "title",
    "핵심 내용": "answer_1",
    "AI의 특징": "answer_2",
    "고객 세그먼트": "answer_3",
    "가치 제안": "answer_4",
    "채널": "answer_5",
    "고객 관계": "answer_6",
    "수익 흐름": "answer_7",
    "핵심 자원": "answer_8",
    "핵심 활동": "answer_9",
    "핵심 파트너십": "answer_10",
    "비용 구조": "answer_11",
    "추가영역 제시": "answer_12",
    "비즈니스 캔버스 모델의 틀을 바꿔 새로운 비즈니스 캔버스 모델을 제시": "answer_13",
    "기타": "answer_14"
}

# 오류 응답 생성 함수
def create_error_response(questions):
    """오류 발생 시 기본 응답을 생성하는 함수"""
    return {
        'results': [
            {
                'question_id': q_id,
                'answer': '처리 중 오류가 발생했습니다. 자세한 내용은 로그를 확인해주세요.'
            }
            for q_id, _ in questions
        ]
    }

# 기본 응답 생성 함수
def create_default_response(questions):
    """기본 응답을 생성하는 함수"""
    return {
        'results': [
            {
                'question_id': q_id,
                'answer': '해당 내용을 찾을 수 없습니다.'
            }
            for q_id, _ in questions
        ]
    }

# 구조화된 답변 생성 함수
def create_structured_answer(question):
    """질문에 맞는 구조화된 답변 템플릿을 생성하는 함수"""
    parts = question.split(':')[1].split('\n') if ':' in question else []
    return '\n'.join([f"{i+1}) {part.strip()}: 해당 내용 없음" for i, part in enumerate(parts) if part.strip()])

# 오류 처리 데코레이터
def error_handler(func):
    """함수 실행 중 발생하는 오류를 처리하는 데코레이터"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"{func.__name__} 실행 중 오류 발생: {str(e)}", exc_info=True)
            if 'questions' in kwargs:
                return create_error_response(kwargs['questions'])
            return None
    return wrapper

@error_handler
def setup_gemini():
    """Gemini API를 설정하고 모델을 초기화합니다.
    
    Returns:
        GenerativeModel: 초기화된 Gemini 모델 객체
        
    Raises:
        Exception: API 키가 유효하지 않거나 모델 초기화에 실패한 경우
    """
    api_key = "AIzaSyB1te7hQnMp6v5nyQgv_F2uUMjTonbSjDs"  # 직접 API 키 설정
    
    genai.configure(api_key=api_key)
    
    # 모델 설정
    generation_config = {
        "temperature": 0.2,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 4096,
    }
    
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    
    try:
        model = genai.GenerativeModel("gemini-2.5-pro-exp-03-25",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        return model
    except Exception as e:
        logging.error(f"모델 초기화 오류: {str(e)}")
        raise

# PDF 파일 읽기 함수
def extract_text_from_pdf(pdf_path):
    """PDF 파일에서 텍스트를 추출합니다.
    
    Args:
        pdf_path (str): PDF 파일의 경로
        
    Returns:
        str: 추출된 텍스트 또는 오류 발생 시 None
        
    Raises:
        Exception: PDF 파일 읽기 실패 시
    """
    try:
        # PyMuPDF를 사용한 텍스트 추출 시도
        with fitz.open(pdf_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            return text
    except Exception as e:
        logging.error(f"PDF 파일 읽기 오류 ({pdf_path}): {str(e)}")
        return None

# 논문 제목 추출 함수
def extract_title(text):
    """논문 텍스트에서 제목을 추출합니다.
    
    Args:
        text (str): 논문의 전체 텍스트
        
    Returns:
        str: 추출된 제목 또는 None
        
    Note:
        - 첫 번째 의미 있는 줄을 제목으로 간주
        - 'abstract', 'introduction' 등의 단어가 포함된 줄은 제외
    """
    try:
        # 텍스트가 없는 경우 처리
        if not text or not text.strip():
            return None
        
        # 첫 번째 의미 있는 줄을 찾음
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 5:  # 최소 길이 조건
                # 일반적인 논문 제목이 아닌 경우 제외
                if not any(skip in line.lower() for skip in ['abstract', 'introduction', 'contents', 'chapter']):
                    return line
        return None
    except Exception as e:
        logging.error(f"제목 추출 오류: {str(e)}")
        return None

def validate_answer_structure(answer, question):
    """답변의 구조를 검증하는 함수"""
    # 필수 구조 확인
    required_parts = question.split(':')
    if len(required_parts) < 2:
        return False
    
    # 각 부분이 존재하는지 확인
    for i in range(1, len(required_parts)):
        if f"{i})" not in answer:
            return False
    
    # 내용의 구체성 확인
    if "해당 내용 없음" in answer:
        return False
    
    return True

def enhance_answer(answer, question):
    """답변의 품질을 향상시키는 함수"""
    # 구조화된 답변 생성
    parts = question.split(':')
    enhanced_parts = []
    
    for i, part in enumerate(parts, 1):
        if f"{i})" in answer:
            # 기존 답변 사용
            enhanced_parts.append(answer.split(f"{i})")[1].split(f"{i+1})")[0].strip())
        else:
            # 새로운 답변 생성
            enhanced_parts.append(f"{part}: 해당 내용 없음")
    
    return "\n".join([f"{i}) {part}" for i, part in enumerate(enhanced_parts, 1)])

def validate_reference_sheet_alignment(answer, question_id):
    """참조 시트와의 일치도를 검증하는 함수"""
    # 참조 시트의 분석 패턴과 비교
    reference_patterns = {
        1: ["연구 목적", "주요 방법론", "핵심 발견사항", "시사점"],
        2: ["기술적 특성", "비즈니스 특성", "시장 특성"],
        3: ["주요 유형", "구체적 예시", "각 세그먼트의 특징"],
        # ... 다른 질문 ID에 대한 패턴 추가
    }
    
    if question_id not in reference_patterns:
        return True
    
    # 각 패턴이 답변에 포함되어 있는지 확인
    for pattern in reference_patterns[question_id]:
        if pattern not in answer:
            return False
    
    return True

def align_with_reference_sheet(answer, question_id):
    """참조 시트와의 일치도를 향상시키는 함수"""
    # 참조 시트의 분석 패턴에 맞게 답변 조정
    reference_patterns = {
        1: ["연구 목적", "주요 방법론", "핵심 발견사항", "시사점"],
        2: ["기술적 특성", "비즈니스 특성", "시장 특성"],
        3: ["주요 유형", "구체적 예시", "각 세그먼트의 특징"],
        # ... 다른 질문 ID에 대한 패턴 추가
    }
    
    if question_id not in reference_patterns:
        return answer
    
    aligned_parts = []
    for pattern in reference_patterns[question_id]:
        if pattern in answer:
            # 기존 답변 사용
            aligned_parts.append(answer.split(pattern)[1].split("\n")[0].strip())
        else:
            # 새로운 답변 생성
            aligned_parts.append(f"{pattern}: 해당 내용 없음")
    
    return "\n".join([f"{i+1}) {part}" for i, part in enumerate(aligned_parts)])

def merge_results(all_results: List[dict], questions: List[Tuple[int, str]]) -> dict:
    """여러 청크의 분석 결과를 병합합니다.
    
    Args:
        all_results (List[dict]): 병합할 결과 리스트
        questions (List[Tuple[int, str]]): 질문 리스트
        
    Returns:
        dict: 병합된 최종 결과
    """
    try:
        # 질문 ID별로 모든 답변을 수집
        answers_by_question = {}
        for result in all_results:
            if not isinstance(result, dict) or 'results' not in result:
                logging.warning("잘못된 결과 형식 무시됨")
                continue
                
            for answer in result['results']:
                if not isinstance(answer, dict) or 'question_id' not in answer or 'answer' not in answer:
                    continue
                    
                q_id = answer['question_id']
                if q_id not in answers_by_question:
                    answers_by_question[q_id] = []
                answers_by_question[q_id].append(answer['answer'])

        # 각 질문에 대한 최종 답변 선택
        final_results = []
        for q_id, q_text in questions:
            if q_id in answers_by_question and answers_by_question[q_id]:
                # 가장 상세한 답변 선택
                best_answer = max(answers_by_question[q_id], key=len)
                final_results.append({
                    'question_id': q_id,
                    'answer': best_answer
                })
            else:
                final_results.append({
                    'question_id': q_id,
                    'answer': "해당 내용을 찾을 수 없습니다."
                })

        return {'results': final_results}

    except Exception as e:
        logging.error(f"결과 병합 중 오류 발생: {str(e)}")
        return create_error_response(questions)

def normalize_response_format(response_text):
    """API 응답을 정규화된 JSON 형식으로 변환합니다."""
    try:
        # JSON 형식이 이미 올바른 경우 바로 반환
        json.loads(response_text)
        return response_text
    except json.JSONDecodeError:
        # JSON 형식이 아닌 경우 정규화 시도
        try:
            # 응답에서 JSON 부분만 추출
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                
                # 이스케이프 문자 처리
                json_str = json_str.replace('\\n', ' ')
                json_str = json_str.replace('\\"', '"')
                json_str = json_str.replace('\\\\', '\\')
                
                # JSON 파싱 시도
                json.loads(json_str)
                return json_str
        except:
            pass
            
        # 정규화 실패 시 기본 형식 반환
        return '{"results": []}'

def analyze_paper(text: str, questions: List[Tuple[int, str]], template: str) -> dict:
    """논문 텍스트를 분석하고 결과를 반환합니다."""
    try:
        # Gemini API 설정
        model = setup_gemini()
        
        # 텍스트를 더 작은 청크로 나누기
        max_chunk_size = 15000  # 약 15KB
        text_chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        
        # 각 청크에 대해 분석 수행
        all_responses = []
        for chunk in text_chunks:
            # 프롬프트 생성
            prompt = create_analysis_prompt(chunk, questions[:1], template)  # 첫 번째 질문만 사용
            logging.debug(f"생성된 프롬프트:\\n{prompt}")
            
            # API 호출 전 대기
            time.sleep(5)  # API 호출 사이에 5초 대기
            
            try:
                # API 호출
                response = model.generate_content(prompt)
                response_text = response.text.strip()
                logging.debug(f"API 응답 전체:\\n{response_text}")
                all_responses.append(response_text)
            except Exception as e:
                logging.error(f"API 호출 중 오류 발생: {str(e)}")
                time.sleep(60)  # 오류 발생 시 1분 대기
                continue
        
        # 모든 응답 결합
        combined_response = " ".join(all_responses)
        
        # JSON 문자열 정규화
        combined_response = combined_response.replace('\\n', ' ').replace('\\r', '')
        combined_response = re.sub(r'\\s+', ' ', combined_response)
        
        # JSON 시작과 끝 부분 찾기
        json_start = combined_response.find('{')
        json_end = combined_response.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = combined_response[json_start:json_end]
            # JSON 검증 및 파싱
            return validate_json_response(json_str)
        else:
            raise ValueError("유효한 JSON 응답을 찾을 수 없습니다.")
            
    except Exception as e:
        logging.error(f"분석 중 오류 발생: {str(e)}")
        raise

def validate_json_structure(result, questions):
    """JSON 구조를 검증하는 유틸리티 함수"""
    try:
        # 기본 구조 검증
        if not isinstance(result, dict):
            logging.error("결과가 딕셔너리가 아닙니다.")
            return False
        if 'results' not in result:
            logging.error("results 키가 없습니다.")
            return False
        if not isinstance(result['results'], list):
            logging.error("results가 리스트가 아닙니다.")
            return False
        
        # 각 결과 항목 검증
        for item in result['results']:
            if not isinstance(item, dict):
                logging.error("결과 항목이 딕셔너리가 아닙니다.")
                return False
            if 'question_id' not in item:
                logging.error("question_id가 없습니다.")
                return False
            if 'answer' not in item:
                logging.error("answer가 없습니다.")
                return False
            if not isinstance(item['question_id'], (int, str)):
                logging.error("question_id가 정수나 문자열이 아닙니다.")
                return False
            if not isinstance(item['answer'], str):
                logging.error("answer가 문자열이 아닙니다.")
                return False
        
        # 모든 질문에 대한 답변이 있는지 확인
        question_ids = {str(q_id) for q_id, _ in questions}
        result_ids = {str(item.get('question_id')) for item in result['results']}
        
        if not question_ids.issubset(result_ids):
            missing_ids = question_ids - result_ids
            logging.error(f"누락된 질문 ID: {missing_ids}")
            return False
        
        return True
        
    except Exception as e:
        logging.error(f"JSON 구조 검증 중 오류: {str(e)}")
        return False

def ensure_directory_exists(directory):
    """디렉토리가 존재하지 않으면 생성합니다."""
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        logging.error(f"디렉토리 생성 중 오류 발생: {str(e)}")
        raise

def save_results_to_csv(results_list, output_path, max_retries=3, retry_delay=5):
    """분석 결과를 CSV 파일로 저장합니다."""
    try:
        # 파일명에 타임스탬프 추가
        base, ext = os.path.splitext(output_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(RESULTS_DIR["raw"], f"{base}_{timestamp}{ext}")
        
        # 출력 디렉토리 생성
        output_dir = os.path.dirname(output_path)
        ensure_directory_exists(output_dir)
        
        # 결과를 DataFrame으로 변환
        df = pd.DataFrame(results_list)
        
        # CSV 파일로 저장
        for attempt in range(max_retries):
            try:
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                logging.info(f"결과가 {output_path}에 저장되었습니다.")
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    logging.error(f"파일 저장 시도 {attempt + 1} 실패: {str(e)}")
                    time.sleep(retry_delay)
                else:
                    logging.error(f"결과 저장 중 오류 발생: {str(e)}")
                    raise
                    
    except Exception as e:
        logging.error(f"결과 저장 중 오류 발생: {str(e)}")
        raise

def process_pdf(pdf_path: str, questions: List[Tuple[int, str]], template: str) -> List[dict]:
    """PDF 파일을 처리하고 분석 결과를 반환합니다.
    
    Args:
        pdf_path (str): PDF 파일 경로
        questions (List[Tuple[int, str]]): 분석 질문 리스트
        template (str): 프롬프트 템플릿
        
    Returns:
        List[dict]: 분석 결과 리스트
    """
    try:
        # PDF에서 텍스트 추출
        text = extract_text_from_pdf(pdf_path)
        if not text:
            logging.error(f"{pdf_path}에서 텍스트를 추출할 수 없습니다.")
            return []
            
        # 전체 텍스트를 그대로 분석
        result = analyze_paper(text, questions, template)
        if result:
            return [result]
        return []
        
    except Exception as e:
        logging.error(f"PDF 처리 중 오류 발생: {str(e)}")
        return []

def main():
    """메인 함수"""
    try:
        # PDF 디렉토리 확인
        if not os.path.exists(PDF_DIR):
            logging.error(f"PDF 디렉토리를 찾을 수 없습니다: {PDF_DIR}")
            return
            
        # PDF 파일 목록 가져오기
        pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]
        if not pdf_files:
            logging.error(f"{PDF_DIR}에 PDF 파일이 없습니다.")
            return
            
        logging.info(f"총 {len(pdf_files)}개의 PDF 파일을 찾았습니다.")
        
        # 테스트를 위해 첫 번째 파일만 처리
        pdf_file = pdf_files[0]
        logging.info(f"테스트를 위해 첫 번째 PDF 파일만 처리합니다: {pdf_file}")
        
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        logging.info(f"PDF 파일 처리 중: {pdf_file}")
        
        # 질문과 템플릿 로드
        questions = load_questions_from_md("prompts.md")
        template = load_prompt_template("prompts.md")
        
        # PDF 처리 및 분석
        results = process_pdf(pdf_path, questions, template)
        
        if not results:
            logging.error(f"{pdf_file} 파일 분석 결과가 없습니다.")
            return
            
        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(RESULTS_DIR["processed"], f"analysis_{os.path.splitext(pdf_file)[0]}_{timestamp}.csv")
        save_results_to_csv(results, output_path)
        
        logging.info("스크립트 실행 완료.")
        
    except Exception as e:
        logging.error(f"메인 함수 실행 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()