import google.generativeai as genai
import pathlib
import csv
import os
import json # JSON 파싱을 위해 추가
from datetime import datetime
import time # 지연 시간 추가를 위해
import logging  # 로깅 모듈 추가

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
                 response_mime_type="application/json" # JSON 응답 요청
            )
            # request_options={'timeout': 300} # Flash 모델은 응답이 빠르므로 타임아웃 줄이기 가능
        )
        logger.info(f"-> Gemini API 응답 수신 완료 ({pdf_file.display_name}).")

        if hasattr(response, 'text'):
            logger.info(f"Gemini 응답 (파일: {pdf_file.display_name}):\n{response.text}")
            return response.text
        else:
            logger.warning(f"경고: '{pdf_file.display_name}' 분석 응답에 텍스트가 없습니다.")
            # 상세 피드백 출력 (이전과 동일)
            if hasattr(response, 'prompt_feedback'): logger.info(f"   Prompt Feedback: {response.prompt_feedback}")
            if hasattr(response, 'candidates'):
                 for i, c in enumerate(response.candidates):
                     if hasattr(c, 'safety_ratings'): logger.info(f"   Candidate {i+1} Safety: {c.safety_ratings}")
            return None

    except Exception as e:
        logger.error(f"오류: '{pdf_file.display_name}' 분석 중 Gemini API 호출 오류 발생 - {e}")
        # Rate limit 오류 감지 시 추가 지연
        if "rate limit" in str(e).lower():
             logger.info("   Rate limit 오류 감지. 다음 호출 전 지연 시간을 늘립니다...")
             time.sleep(API_CALL_DELAY * 5) # 잠시 대기
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

def main(pdf_path: str, prompt_template: str, csv_fieldnames: list):
    """메인 실행 함수: PDF 업로드, 분석, 결과 반환 (단일 파일 처리)"""
    pdf_filename = pathlib.Path(pdf_path).name
    result_data = {field: "처리 시작" for field in csv_fieldnames} # 초기 상태 설정
    result_data["논문 제목"] = pdf_filename
    result_data["오류"] = "" # 오류 메시지 필드 초기화

    # 1. PDF 파일 업로드
    uploaded_file = upload_pdf_to_gemini(pdf_path)
    if not uploaded_file:
        result_data["오류"] = "파일 업로드 실패"
        # 다른 필드 상태 업데이트
        for field in csv_fieldnames:
            if field not in ["논문 제목", "오류"]: result_data[field] = "처리 중단 (업로드 실패)"
        return result_data # 업로드 실패 시 오류 정보 포함하여 반환

    prompt = prompt_template

    # API 호출 전 지연 (Rate Limit 방지)
    # print(f"-> API 호출 전 {API_CALL_DELAY}초 대기...")
    time.sleep(API_CALL_DELAY)

    # 2. Gemini API로 분석 요청
    analysis_response_text = analyze_pdf_with_gemini(uploaded_file, prompt)

    # 3. 결과 처리
    if analysis_response_text:
        try:
            analysis_data = json.loads(analysis_response_text)
            # 리스트 형태의 응답이면 모든 항목을 합침
            if isinstance(analysis_data, list):
                merged_data = {}
                for item in analysis_data:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if key not in merged_data:
                                merged_data[key] = value
                            elif merged_data[key] == "정보 없음" and value != "정보 없음":
                                merged_data[key] = value
                            elif isinstance(merged_data[key], str) and isinstance(value, str):
                                merged_data[key] = f"{merged_data[key]}\n{value}"
                analysis_data = merged_data
            
            for field in csv_fieldnames:
                if field in ["논문 제목", "오류"]: continue
                json_value = analysis_data.get(field)
                result_data[field] = json_value if json_value not in [None, ""] else "정보 없음"
            result_data["오류"] = "" # 성공적으로 처리되면 오류 메시지 없음

        except json.JSONDecodeError:
            logger.warning(f"경고: '{pdf_filename}' 응답 파싱 실패. 원본 텍스트를 '핵심 내용'에 저장.")
            result_data["오류"] = "JSON 파싱 오류"
            for field in csv_fieldnames:
                 if field not in ["논문 제목", "오류", "핵심 내용"]: result_data[field] = "JSON 파싱 오류"
            result_data["핵심 내용"] = analysis_response_text # 핵심 내용에 원본 저장
        except Exception as e:
            logger.error(f"오류: '{pdf_filename}' 응답 데이터 처리 중 예기치 않은 오류 - {e}")
            result_data["오류"] = f"데이터 처리 오류: {e}"
            for field in csv_fieldnames:
                 if field not in ["논문 제목", "오류"]: result_data[field] = "데이터 처리 오류"
    else:
        logger.warning(f"경고: '{pdf_filename}' 분석 결과 없음 (API 응답 없음 또는 오류).")
        result_data["오류"] = "API 응답 없음"
        for field in csv_fieldnames:
            if field not in ["논문 제목", "오류"]: result_data[field] = "API 응답 없음"

    # (선택 사항) 파일 삭제 로직 (주석 처리됨)
    # ... (이전 코드와 동일) ...

    return result_data # 최종 처리 결과 반환

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
        "논문 제목", "핵심 내용", "AI의 특징", "고객 세그먼트", "가치 제안",
        "채널", "고객 관계", "수익 흐름", "핵심 자원", "핵심 활동",
        "핵심 파트너십", "비용 구조", "추가영역 제시",
        "비즈니스 캔버스 모델의 틀을 바꿔 새로운 비즈니스 캔버스 모델을 제시", "기타", "오류"
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

각 키에 대해 다음 질문들을 **이 문서에서 다루는 핵심 AI 서비스와 그 비즈니스 모델 관점**에서 고려하여 내용을 채워주세요:

- "핵심 내용": 이 문서에서 분석하는 **핵심 AI 서비스**는 무엇이며, 이 문서가 해당 서비스의 **비즈니스 모델 캔버스(BMC)를 분석하는 주요 목적이나 맥락**은 무엇인지 요약해주세요. (예: 특정 AI 서비스의 BMC 구성 요소 분석, AI 기반 비즈니스 모델 유형 연구 등)
- "AI의 특징": 이 AI 서비스의 **핵심 기술(알고리즘, 학습 데이터 등)과 주요 기능**은 무엇이며, 이러한 특징이 **비즈니스 모델의 다른 요소(예: 가치 제안, 비용 구조, 핵심 자원)에 미치는 영향**은 어떻게 설명되어 있나요? (AI 기술 자체의 경쟁 우위나 차별점도 포함)
- "고객 세그먼트": 이 AI 서비스가 **타겟하는 주요 고객 세그먼트(B2B/B2C, 특정 산업, 사용자 역할 등)**는 누구이며, 문서에 **구체적인 고객 사례나 각 세그먼트가 AI 서비스를 통해 얻고자 하는 구체적인 니즈/문제점**이 언급되어 있나요?
- "가치 제안": 이 AI 서비스가 각 고객 세그먼트에게 제공하는 **핵심적인 가치(어떤 문제를 해결하거나 어떤 편익을 주는가?)**는 무엇이며, **AI 기술(예: 자동화, 예측, 개인화)이 어떻게 이 가치를 창출하거나 강화하는지** 설명되어 있나요? (경쟁 서비스 대비 차별화된 가치 포함)
- "채널": 이 AI 서비스를 목표 고객에게 **인지시키고, 가치를 전달하며(예: API, 웹 앱, 임베디드), 판매 후 관계를 유지하기 위해 사용하는 채널**(온라인 플랫폼, 파트너 네트워크, 직접 영업, 개발자 커뮤니티 등)은 무엇인가요? 각 채널의 역할과 특징을 설명해주세요.
- "고객 관계": 이 AI 서비스가 주요 고객 세그먼트와 **구축하고 유지하려는 관계의 유형**(예: 셀프 서비스, 자동화된 지원(챗봇), 전담 지원, 커뮤니티 운영)은 무엇이며, 이를 위해 **AI 기술을 활용한 구체적인 전략이나 기능**(예: 맞춤형 추천, 예측적 유지보수 알림)이 사용되나요?
- "수익 흐름": 이 AI 서비스로부터 발생하는 **주요 수익원과 가격 책정 모델**(예: 구독료, 사용량 기반 과금(API 호출 수, 데이터 처리량), 라이선스 판매, 결과 기반 과금, 부가 서비스 판매)은 무엇인가요? **AI의 특징(예: 학습 데이터의 가치, 예측 정확도)이 수익 모델 설계에 미치는 영향**이 언급되어 있나요?
- "핵심 자원": 이 AI 서비스를 제공하는 데 **가장 중요하고 차별화되는 핵심 자원**(예: 독점적인 AI 모델/알고리즘, 대규모/고품질 학습 데이터셋, AI 전문 인력, 특화된 기술 인프라, 강력한 브랜드)은 무엇인가요? **데이터나 AI 모델 자체가 핵심 자원으로서 어떻게 강조**되나요?
- "핵심 활동": 이 AI 서비스를 개발, 운영, 개선하기 위해 수행해야 하는 **가장 중요한 활동**(예: AI 모델 연구개발 및 학습, 데이터 수집/정제/관리, 플랫폼 운영 및 확장, 고객 데이터 분석, 규제 준수 활동)은 무엇인가요? 특히 **지속적인 AI 성능 개선 및 유지보수**와 관련된 활동을 설명해주세요.
- "핵심 파트너십": 이 AI 서비스의 성공적인 제공을 위해 **의존하는 주요 외부 파트너 유형**(예: 클라우드 인프라 제공자(AWS, GCP, Azure), 데이터 공급자, 기술 협력사, 특정 산업 도메인 전문가, 채널 파트너)은 누구이며, **파트너십을 통해 어떤 핵심 자원을 확보하거나 어떤 핵심 활동을 수행**하나요?
- "비용 구조": 이 AI 서비스를 제공하는 데 발생하는 **주요 비용 항목과 그 특징**(예: AI 연구개발 인건비, 대규모 GPU 등 컴퓨팅 자원 비용, 데이터 구매/저장 비용, 모델 유지보수 비용, 고객 확보 비용)은 무엇인가요? **AI 기술로 인해 발생하는 특유의 비용(예: 높은 초기 투자, 지속적인 모델 업데이트 비용)이나 비용 절감 기회**가 언급되었나요? (가치 중심 vs 비용 중심 구조)
- "추가영역 제시": 문서 저자가 **AI 서비스의 특수성을 반영하기 위해 기존 BMC에 추가하거나 수정해야 한다고 제안하는 새로운 영역이나 요소**(예: 데이터 거버넌스, 윤리적 고려사항, 모델 유지보수 활동 등)가 있나요? 있다면 그 내용과 제안 배경, 예상 효과는 무엇인가요?
- "비즈니스 캔버스 모델의 틀을 바꿔 새로운 비즈니스 캔버스 모델을 제시": 문서 저자가 **AI 서비스에 더 적합하다고 주장하며 기존 BMC와 다른 새로운 프레임워크나 수정된 캔버스 모델**을 제시하나요? 그렇다면 그 모델의 구체적인 구성 요소, 기존 모델과의 주요 차이점, 그리고 AI 서비스 분석에 이 모델이 더 유용하다고 주장하는 이유는 무엇인가요?
- "기타": 위 항목 외에 이 **AI 서비스의 비즈니스 모델 분석과 관련하여 문서에서 특별히 강조하거나 중요하게 다루는 통찰, 성공/실패 요인 분석, 시장 동향, 경쟁 환경, 규제 문제, 윤리적 고려사항, 또는 향후 발전 방향** 등이 있다면 요약해주세요.

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