import re
import json
from typing import List, Tuple
import logging

def escape_template_braces(template: str) -> str:
    """템플릿의 중괄호를 이스케이프 처리하는 함수"""
    # 이미 이스케이프된 중괄호는 건너뛰기
    escaped = template.replace('{{', '{{{{').replace('}}', '}}}}')
    return escaped

def load_questions_from_md(md_file: str) -> List[Tuple[int, str]]:
    """Markdown 파일에서 질문 목록을 로드하는 함수"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 질문 섹션 추출
    questions_section = re.search(r'# 분석 질문\n\n(.*?)(?=\n#|\Z)', content, re.DOTALL)
    if not questions_section:
        raise ValueError("질문 섹션을 찾을 수 없습니다.")
    
    questions_text = questions_section.group(1)
    
    # 질문 파싱
    questions = []
    current_question = None
    current_parts = []
    
    for line in questions_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # 질문 번호와 내용 추출
        match = re.match(r'(\d+)\.\s+(.*?)$', line)
        if match:
            if current_question:
                questions.append((current_question[0], '\n'.join(current_parts)))
            current_question = (int(match.group(1)), match.group(2))
            current_parts = [match.group(2)]
        elif line.startswith('-'):
            part = line[1:].strip()
            current_parts.append(part)
    
    # 마지막 질문 추가
    if current_question:
        questions.append((current_question[0], '\n'.join(current_parts)))
    
    return questions

def load_prompt_template(md_file: str) -> str:
    """Markdown 파일에서 프롬프트 템플릿을 로드하는 함수"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 프롬프트 템플릿 섹션 추출 (JSON 예시 포함)
    template_section = re.search(r'# 분석 템플릿\n\n(.*?)(?=\n#|\Z)', content, re.DOTALL)
    if not template_section:
        raise ValueError("프롬프트 템플릿을 찾을 수 없습니다.")
    
    template = template_section.group(1).strip()
    return template

def create_analysis_prompt(text: str, questions: List[Tuple[int, str]], template: str) -> str:
    """프롬프트 템플릿을 사용하여 분석 프롬프트를 생성하는 함수"""
    try:
        # 질문 문자열 생성
        questions_str = "\n".join([f"{id}. {q}" for id, q in questions])
        
        # JSON 예시 부분을 제외한 나머지 템플릿만 포맷팅
        template_parts = template.split('응답 형식:')
        if len(template_parts) != 2:
            raise ValueError("템플릿 형식이 올바르지 않습니다.")
            
        # 첫 번째 부분 포맷팅
        formatted_first_part = template_parts[0].format(text=text, questions_str=questions_str)
        
        # 전체 템플릿 재조합
        return formatted_first_part + '응답 형식:' + template_parts[1]
        
    except Exception as e:
        logging.error(f"프롬프트 생성 중 오류 발생: {str(e)}")
        raise

def create_error_response(questions: List[Tuple[int, str]]) -> dict:
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

def create_default_response(questions: List[Tuple[int, str]]) -> dict:
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

def create_structured_answer(question: str) -> str:
    """질문에 맞는 구조화된 답변 템플릿을 생성하는 함수"""
    parts = question.split(':')[1].split('\n') if ':' in question else []
    return '\n'.join([f"{i+1}) {part.strip()}: 해당 내용 없음" for i, part in enumerate(parts) if part.strip()])

def validate_json_response(response_text: str) -> dict:
    """API 응답의 JSON 형식을 검증하고 수정하는 함수"""
    try:
        # JSON 부분 추출
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        json_matches = list(re.finditer(json_pattern, response_text))
        
        for match in json_matches:
            try:
                # JSON 문자열 정리
                json_str = match.group()
                
                # 줄바꿈 문자를 공백으로 변환
                json_str = json_str.replace('\n', ' ').replace('\r', ' ')
                
                # 불필요한 공백 제거
                json_str = re.sub(r'\s+', ' ', json_str)
                
                # 속성 이름에 쌍따옴표 추가
                json_str = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
                
                # 작은따옴표를 큰따옴표로 변환
                json_str = json_str.replace("'", '"')
                
                # 이스케이프된 큰따옴표 처리
                json_str = json_str.replace('\\"', '"')
                json_str = json_str.replace('""', '"')
                
                # 중복된 공백 제거
                json_str = ' '.join(json_str.split())
                
                try:
                    result = json.loads(json_str)
                    if isinstance(result, dict) and "results" in result:
                        return result
                except json.JSONDecodeError as e:
                    logging.debug(f"JSON 파싱 시도 실패: {str(e)}")
                    continue
            except Exception as e:
                logging.debug(f"JSON 문자열 처리 중 오류: {str(e)}")
                continue
                
        logging.error("유효한 JSON 형식을 찾을 수 없습니다.")
        return {"results": []}
        
    except Exception as e:
        logging.error(f"JSON 검증 중 오류 발생: {str(e)}")
        return {"results": []} 