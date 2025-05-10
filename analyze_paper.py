import google.generativeai as genai
import pathlib
import csv
import os
import json # JSON 파싱을 위해 추가
from datetime import datetime
import time # 지연 시간 추가를 위해
import logging  # 로깅 모듈 추가
import re  # JSON 보정용 정규식 추가

# --- 설정 ---
# 1. Gemini API 키 설정 (코드에 직접 입력)
# !!! 중요: API 키를 코드에 직접 넣는 것은 보안상 권장되지 않습니다. !!!
# !!! 코드를 공유하거나 버전 관리 시스템(Git 등)에 올릴 때 키가 노출될 수 있습니다. !!!
# 아래 "YOUR_API_KEY" 부분을 실제 API 키로 교체해주세요.
API_KEY = "AIzaSyB1te7hQnMp6v5nyQgv_F2uUMjTonbSjDs" # <--- 여기에 실제 Google AI Studio 또는 Cloud Console에서 발급받은 API 키를 입력하세요.

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gemini_responses.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

if API_KEY == "YOUR_API_KEY":
    logger.error("오류: 코드 내 API_KEY 변수에 실제 Gemini API 키를 입력해주세요.")
    exit()
try:
    genai.configure(api_key=API_KEY)
    logger.info("Gemini API 키가 설정되었습니다.")
except Exception as e:
    logger.error(f"오류: API 키 설정 중 문제가 발생했습니다 - {e}")
    exit()

# 2. 사용할 Gemini 모델 설정
# 사용자 요청: gemini-2.0-flash. 현재(2025-05-05 기준) 해당 모델명이 공식적으로 확인되지 않아,
# 가장 유사한 최신 flash 모델인 'gemini-1.5-flash-latest'를 사용합니다.
# 만약 'gemini-2.0-flash' 모델이 실제로 출시되었다면 아래 모델명을 수정해주세요.
MODEL_NAME = "gemini-2.0-flash"
logger.info(f"사용할 Gemini 모델: {MODEL_NAME} (사용자 요청 'gemini-2.0-flash' 기반)")

# 3. PDF 파일이 있는 폴더 경로 설정
INPUT_FOLDER_PATH = "input" # 현재 스크립트 파일과 같은 위치에 있는 'input' 폴더

# 4. 결과를 저장할 폴더 경로 설정
OUTPUT_FOLDER_PATH = "result" # 현재 스크립트 파일과 같은 위치에 'result' 폴더 생성 예정

# 5. 결과를 저장할 CSV 파일 경로 (출력 폴더 포함)
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_FILENAME = f"논문분석_결과_{current_time}.csv"
CSV_FILE_PATH = pathlib.Path(OUTPUT_FOLDER_PATH) / CSV_FILENAME

# 6. API 호출 간 지연 시간 (초) - Rate Limit 방지용
API_CALL_DELAY = 2 # Flash 모델은 Rate Limit이 더 높을 수 있으므로 짧게 설정 (필요시 조절)
# --- 설정 끝 ---

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
        return pdf_file
    except Exception as e:
        logger.error(f"오류: '{path.name}' 파일 업로드 중 문제 발생 - {e}")
        # Rate limit 오류 발생 시 약간의 대기 후 재시도 로직 추가 가능
        if "rate limit" in str(e).lower():
             logger.info("   Rate limit 오류 감지. 잠시 후 재시도합니다...")
             time.sleep(API_CALL_DELAY * 5) # 잠시 대기
             # 재시도 로직은 복잡해질 수 있어 여기서는 생략
        return None

def analyze_pdf_with_gemini(pdf_file: genai.types.File, prompt: str) -> str | None:
    """업로드된 PDF 파일과 프롬프트를 사용하여 Gemini API로 분석을 요청합니다."""
    if not pdf_file:
        logger.error("오류: 분석을 위한 유효한 PDF 파일 객체가 없습니다.")
        return None

    logger.info(f"-> Gemini API 호출 중 (모델: {MODEL_NAME}, 파일: {pdf_file.display_name})...")
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(
            [prompt, pdf_file],
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,  # 응답의 다양성을 위한 temperature 설정
                top_p=0.8,       # 응답의 일관성을 위한 top_p 설정
                top_k=40         # 응답의 품질을 위한 top_k 설정
            )
        )
        logger.info(f"-> Gemini API 응답 수신 완료 ({pdf_file.display_name}).")

        if hasattr(response, 'text'):
            # 응답 텍스트를 UTF-8로 인코딩하여 처리
            response_text = response.text.encode('utf-8').decode('utf-8')
            logger.info(f"Gemini 응답 (파일: {pdf_file.display_name}):\n{response_text}")
            return response_text
        else:
            logger.warning(f"경고: '{pdf_file.display_name}' 분석 응답에 텍스트가 없습니다.")
            if hasattr(response, 'prompt_feedback'): 
                logger.info(f"   Prompt Feedback: {response.prompt_feedback}")
            if hasattr(response, 'candidates'):
                for i, c in enumerate(response.candidates):
                    if hasattr(c, 'safety_ratings'): 
                        logger.info(f"   Candidate {i+1} Safety: {c.safety_ratings}")
            return None

    except Exception as e:
        logger.error(f"오류: '{pdf_file.display_name}' 분석 중 Gemini API 호출 오류 발생 - {e}")
        if "rate limit" in str(e).lower():
            logger.info("   Rate limit 오류 감지. 다음 호출 전 지연 시간을 늘립니다...")
            time.sleep(API_CALL_DELAY * 5)
        return None

def save_to_csv(file_path: pathlib.Path, data: dict, fieldnames: list):
    """분석 결과를 CSV 파일에 저장합니다."""
    # 파일 경로는 pathlib.Path 객체로 받음
    file_exists = file_path.exists()
    try:
        # encoding='utf-8-sig' 는 Excel 호환성을 위함
        with open(file_path, 'a', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
                logger.info(f"CSV 파일 '{file_path}' 생성 및 헤더 작성 완료.")
            row_data = {field: data.get(field, "") for field in fieldnames}
            writer.writerow(row_data)
        return True
    except Exception as e:
        logger.error(f"오류: CSV 파일 '{file_path}' 저장 중 문제 발생 - {e}")
        return False

def extract_json(text):
    """JSON 문자열을 추출하고 파싱합니다."""
    try:
        # 1. JSON 문자열 추출
        json_match = re.search(r'```json\s*({[\s\S]*?})\s*```', text)
        if not json_match:
            return None
        
        json_str = json_match.group(1)
        
        # 2. 제어 문자 제거 및 정제
        json_str = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', json_str)  # 제어 문자 제거
        json_str = re.sub(r',\s*}', '}', json_str)  # 마지막 쉼표 제거
        json_str = re.sub(r',\s*]', ']', json_str)  # 배열의 마지막 쉼표 제거
        
        # 3. JSON 파싱
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {str(e)}")
            # 실패한 경우 추가 정제 시도
            json_str = re.sub(r'[\u0000-\u001F\u007F-\u009F]', '', json_str)
            json_str = re.sub(r'\\[^"\\/bfnrtu]', '', json_str)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.error("JSON 파싱 재시도 실패")
                return None
            
    except Exception as e:
        logger.error(f"JSON 추출 실패: {str(e)}")
        return None

def main(pdf_path: str, prompt_template: str, csv_fieldnames: list):
    """메인 실행 함수: PDF 업로드, 분석, 결과 반환 (단일 파일 처리)"""
    pdf_filename = pathlib.Path(pdf_path).name
    result_data = {field: "처리 시작" for field in csv_fieldnames}
    result_data["논문 제목"] = pdf_filename
    result_data["오류"] = ""

    # 1. PDF 파일 업로드
    uploaded_file = upload_pdf_to_gemini(pdf_path)
    if not uploaded_file:
        result_data["오류"] = "파일 업로드 실패"
        for field in csv_fieldnames:
            if field not in ["논문 제목", "오류"]:
                result_data[field] = "처리 중단 (업로드 실패)"
        return result_data

    prompt = prompt_template
    time.sleep(API_CALL_DELAY)

    # 2. Gemini API로 분석 요청
    analysis_response_text = analyze_pdf_with_gemini(uploaded_file, prompt)

    # 3. 결과 처리
    if analysis_response_text:
        try:
            # JSON 추출 및 파싱
            analysis_data = extract_json(analysis_response_text)
            if not analysis_data:
                result_data["오류"] = "JSON 추출 실패"
                return result_data
            
            # 리스트 형태의 응답 처리
            if isinstance(analysis_data, list):
                merged_data = {}
                for item in analysis_data:
                    if isinstance(item, dict):
                        merged_data.update(item)
                analysis_data = merged_data

            # 결과 데이터 업데이트
            for field in csv_fieldnames:
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

    # CSV 컬럼 정의 (오류 컬럼 포함 확인)
    csv_columns = [
        "논문 제목", "핵심 내용", "비즈니스 모델 캔버스(BMC) 활용 여부", "AI의 특징", "고객 세그먼트", 
        "가치 제안", "채널", "고객 관계", "수익 흐름", "핵심 자원", "핵심 활동",
        "핵심 파트너십", "비용 구조", "추가영역 제시",
        "비즈니스 캔버스 모델의 틀을 바꿔 새로운 비즈니스 캔버스 모델을 제시",
        "기타", "오류"
    ]
    if "오류" not in csv_columns: csv_columns.append("오류")

    # Gemini 프롬프트
    prompt_keys = csv_columns[1:-1] # Index 1부터 마지막-1까지
    analysis_prompt = f"""
이 PDF 논문 내용을 분석하여, 아래 명시된 각 키(key)에 해당하는 내용을 추출하고 **반드시 유효한 JSON 형식**으로 응답해주세요.
각 키에 대한 값(value)은 논문 내용을 기반으로 상세하게 작성해주세요.
만약 논문에서 특정 키에 해당하는 내용을 찾을 수 없거나 명확하지 않은 경우, 해당 키의 값으로 "정보 없음" 또는 `null`을 사용해주세요.

JSON 형식의 키는 다음과 같습니다:
{json.dumps(prompt_keys, ensure_ascii=False)}

각 키에 대해 다음 질문들을 고려하여 내용을 채워주세요:

1. "핵심 내용": 논문의 초록(Abstract), 서론(Introduction), 결론(Conclusion) 부분을 참고하여 논문이 다루는 주요 연구 내용, 목적, 방법론, 핵심 주장, 결과 및 기여점 등을 2-3 문장으로 요약해주세요.

2. "비즈니스 모델 캔버스(BMC) 활용 여부": 이 논문에서 비즈니스 모델 캔버스(BMC) 또는 그 변형된 형태를 연구의 방법론, 분석틀, 결과 제시 등 어떤 방식으로든 활용하였는지 여부를 'Y' 또는 'N'으로 표시하십시오. 만약 활용했다면('Y'인 경우), 어떤 맥락에서 BMC가 사용되었는지 간략히 언급합니다.

3. "AI의 특징": 논문에서 연구 대상 AI 기술 또는 시스템이 가지는 주요 기술적, 기능적, 또는 개념적 특징으로 언급된 부분을 찾아 요약해주세요 (예: 텍스트 생성 능력, 자동화, 데이터 분석, 예측 분석, 편향성 가능성 등). 논문 전체에서 관련 내용을 참고해주세요.

4. "고객 세그먼트": 논문에서 제안하거나 분석하는 솔루션, 기술, 또는 모델의 주요 사용자, 수혜자, 또는 대상 그룹으로 언급된 부분을 찾아 기입해주세요. (비즈니스 모델 논문이 아니더라도, 기술의 적용 대상이나 영향을 받는 집단을 이 항목에 기입할 수 있습니다.)

5. "가치 제안": 논문에서 제안하거나 분석하는 솔루션, 기술, 또는 모델이 제공하는 핵심적인 가치, 혜택, 또는 해결하는 문제점으로 설명된 부분을 찾아 기입해주세요 (예: 효율성 증대, 비용 절감, 의사결정 지원, 새로운 기능 제공 등).

6. "채널": 논문에서 제안하거나 분석하는 솔루션, 기술, 모델이 사용자에게 전달되거나 소통하는 경로로 언급된 부분이 있다면 기입해주세요 (예: 특정 플랫폼, API, 사용자 인터페이스, 교육 프로그램 등).

7. "고객 관계": 논문에서 제안하거나 분석하는 솔루션, 기술, 모델과 사용자 간의 상호작용 방식이나 관계 구축 방식으로 언급된 부분이 있다면 기입해주세요 (예: 자동화된 지원, 맞춤형 서비스 제공, 피드백 루프 등).

8. "수익 흐름": 논문에서 기술이나 모델의 수익 창출 방식, 자금 조달 방식, 또는 경제적 영향과 관련하여 언급된 부분이 있다면 기입해주세요 (예: 정부 예산, 구독 모델, 라이선스, 연구 보조금 등). (비즈니스 모델 논문이 아니더라도, 운영 비용이나 재정 관련 언급을 참고할 수 있습니다.)

9. "핵심 자원": 논문에서 제안하거나 분석하는 솔루션, 기술, 모델의 구현 및 운영에 필요한 핵심 자원으로 언급된 부분을 찾아 기입해주세요 (예: 전문 인력, 데이터셋, 컴퓨팅 인프라, 특정 알고리즘, 파트너십 등).

10. "핵심 활동": 논문에서 제안하거나 분석하는 솔루션, 기술, 모델을 개발, 구현, 운영하기 위해 필요한 주요 활동으로 언급된 부분을 찾아 기입해주세요 (예: 연구 개발, 데이터 처리, 모델 학습, 시스템 배포, 사용자 교육 등).

11. "핵심 파트너십": 논문에서 기술 개발, 구현, 또는 적용을 위해 협력하는 주요 파트너 또는 이해관계자로 언급된 부분이 있다면 기입해주세요 (예: 기술 기업, 연구 기관, 정부 부처, NGO 등).

12. "비용 구조": 논문에서 기술 개발, 구현, 운영과 관련하여 발생하는 주요 비용 항목이나 잠재적 비용 문제로 언급된 부분이 있다면 기입해주세요 (예: 인건비, 인프라 비용, 유지보수 비용, 라이선스 비용 등).

13. "추가영역 제시": 논문에서 전통적인 분석 틀(예: 비즈니스 모델 캔버스) 외에 해당 연구 주제(예: AI 솔루션, 특정 분야 적용)의 특징을 설명하기 위해 특별히 강조하거나 추가적으로 제시한 분석 관점 또는 고려 사항이 있는지 확인하고, 있다면 해당 내용과 그 이유를 간략히 설명해주세요 (예: 윤리적 고려사항, 핵심 지표, 잠재적 과제 등).

14. "비즈니스 캔버스 모델의 틀을 바꿔 새로운 비즈니스 캔버스 모델을 제시": 논문이 기존의 잘 알려진 프레임워크(예: 오스터왈더의 비즈니스 모델 캔버스)의 구성요소나 구조 자체를 명시적으로 변경하여 새로운 형태의 분석 틀을 제안하고 있는지 판단하여 'Y' 또는 'N'으로 표시해주세요.

15. "기타": 위 항목 외에 논문 분석 과정에서 발견된 특이사항이나 중요하다고 생각되는 추가 정보(예: 연구의 한계점, 주요 논쟁점, 향후 연구 방향 제시 등)를 자유롭게 기입해주세요.

*응답은 반드시 다른 설명 없이 JSON 객체({ ... })만 포함해야 합니다.**
"""

    # 모든 파일 처리
    for pdf_file in pdf_files:
        try:
            logger.info(f"\n--- 파일 처리 시작: {pdf_file.name} ---")
            result = main(str(pdf_file), analysis_prompt, csv_columns)
            if save_to_csv(CSV_FILE_PATH, result, csv_columns):
                logger.info(f"-> 결과 저장 완료: {pdf_file.name}")
            else:
                logger.error(f"오류: '{pdf_file.name}' 처리 결과를 CSV에 저장하지 못했습니다.")
        except Exception as e:
            logger.error(f"오류: '{pdf_file.name}' 처리 중 예기치 못한 문제 발생 - {e}")

    end_time = datetime.now()
    logger.info(f"\n--- 작업 완료: {end_time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    logger.info(f"처리 시간: {end_time - start_time}")
    logger.info(f"결과는 '{CSV_FILE_PATH}' 파일에서 확인하세요.")